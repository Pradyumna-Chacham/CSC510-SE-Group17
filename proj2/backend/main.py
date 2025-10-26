from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
import sqlite3
import os
import json
import re
from typing import List
from db import init_db
from sentence_transformers import SentenceTransformer, util
from rag_utils import semantic_chunk, init_vector_db, add_chunks_to_db, retrieve_chunks

app = FastAPI()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Initialize SQLite ---
init_db()

# --- Schemas ---
class UseCaseSchema(BaseModel):
    title: str
    preconditions: List[str]
    main_flow: List[str]
    sub_flows: List[str]
    alternate_flows: List[str]
    outcomes: List[str]
    stakeholders: List[str]

class InputText(BaseModel):
    raw_text: str

# --- Load LLaMA 3.2 3B Instruct ---
MODEL_NAME = "meta-llama/Llama-3.2-3B-Instruct"
token = os.getenv("HF_TOKEN")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_auth_token=token)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto",
    use_auth_token=token
)
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device_map="auto")

# --- Vector DB for RAG ---
vector_db = init_vector_db()

# --- JSON extraction & flattening ---
import json, re

def extract_json(text: str):
    """
    Extracts valid JSON arrays or objects from LLM output.
    If none found, heuristically parses numbered text sections into JSON objects.
    """
    cleaned = (
        text.replace("```json", "")
            .replace("```", "")
            .replace("\n\n", "\n")
            .strip()
    )

    matches = re.findall(r'(\[[\s\S]*?\]|\{[\s\S]*?\})', cleaned)
    parsed_blocks = []

    for m in matches:
        try:
            parsed = json.loads(m)
        except json.JSONDecodeError:
            repaired = (
                m.replace("None", "null")
                .replace("True", "true")
                .replace("False", "false")
            )
            repaired = re.sub(r",(\s*[\]}])", r"\1", repaired)
            try:
                parsed = json.loads(repaired)
            except json.JSONDecodeError:
                continue
        if isinstance(parsed, dict):
            parsed_blocks.append(parsed)
        elif isinstance(parsed, list):
            parsed_blocks.extend([p for p in parsed if isinstance(p, dict)])

    # ✅ fallback parser for plain-text structured output
    if not parsed_blocks:
        blocks = re.split(r'\n\s*\d+\.\s+', cleaned)
        for block in blocks:
            if not block.strip():
                continue
            title_match = re.match(r'([A-Z][^\n]+)', block.strip())
            if not title_match:
                continue
            title = title_match.group(1).strip()
            fields = dict(re.findall(r'-\s*([^:]+):\s*(.*)', block))
            parsed_blocks.append({
                "title": title,
                "preconditions": [fields.get("Preconditions", "").strip()],
                "main_flow": [fields.get("Main Flow", "").strip()],
                "sub_flows": [fields.get("Sub Flows", "").strip()],
                "alternate_flows": [fields.get("Alternate Flows", "").strip()],
                "outcomes": [fields.get("Outcomes", "").strip()],
                "stakeholders": [fields.get("Stakeholders", "").strip()],
            })

    if not parsed_blocks:
        raise ValueError("No valid JSON found.")
    return parsed_blocks


def flatten_use_case(data: dict) -> dict:
    flat = {}
    flat["title"] = data.get("title", "Untitled")

    def ensure_list(value, placeholder=None):
        if isinstance(value, list):
            return [str(v) for v in value] or ([placeholder] if placeholder else [])
        elif isinstance(value, dict):
            return [f"{k}: {v}" for k, v in value.items()] or ([placeholder] if placeholder else [])
        elif value:
            return [str(value)]
        else:
            return [placeholder] if placeholder else []

    flat["preconditions"] = ensure_list(data.get("preconditions"), "No preconditions")
    flat["main_flow"] = ensure_list(data.get("main_flow"), "No main flow")
    flat["sub_flows"] = ensure_list(data.get("sub_flows"), "No subflows")
    flat["alternate_flows"] = ensure_list(data.get("alternate_flows"), "No alternate flows")
    flat["outcomes"] = ensure_list(data.get("outcomes"), "No outcomes")
    flat["stakeholders"] = ensure_list(data.get("stakeholders"), "No stakeholders")
    return flat


# Initialize embedding model for duplicate detection
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def compute_usecase_embedding(use_case: UseCaseSchema):
    """Combine title and main_flow into a single embedding vector."""
    text = use_case.title + " " + " ".join(use_case.main_flow)
    return embedder.encode(text, convert_to_tensor=True)

@app.post("/parse_use_case_rag/")
def parse_use_case_rag(request: InputText):
    chunks = semantic_chunk(request.raw_text)
    add_chunks_to_db(vector_db, chunks)
    db_path = os.path.join(os.path.dirname(__file__), "requirements.db")
    
    all_use_cases = []
    for chunk in chunks:
        retrieved = retrieve_chunks(vector_db, chunk, n_results=3)
        context = "\n".join(retrieved)

        prompt = f"""
You are a senior software analyst.

From the text below, extract ALL distinct use cases.

Each use case must be a JSON object with these fields:
"title", "preconditions", "main_flow", "sub_flows", "alternate_flows", "outcomes", "stakeholders".

Return ONLY a valid JSON array.
Text:
{context}
"""
        llm_output = pipe(
            prompt,
            max_new_tokens=900,
            temperature=0.5,
            top_p=0.9,
            repetition_penalty=1.1,
            eos_token_id=tokenizer.eos_token_id
        )[0]["generated_text"]

        try:
            json_objs = extract_json(llm_output)
            for obj in json_objs:
                flat = flatten_use_case(obj)
                all_use_cases.append(UseCaseSchema(**flat))
        except Exception as e:
            all_use_cases.append({
                "status": "error",
                "details": str(e),
                "raw_output": llm_output
            })

    # --- Phase 1: remove duplicates within current request ---
    unique_titles = set()
    filtered_use_cases = []
    for uc in all_use_cases:
        if isinstance(uc, dict):  # keep errors
            filtered_use_cases.append(uc)
            continue
        if uc.title.lower() not in unique_titles:
            filtered_use_cases.append(uc)
            unique_titles.add(uc.title.lower())

    # --- Phase 2: check duplicates across DB using semantic similarity ---
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT title, main_flow FROM use_cases")
    existing_rows = c.fetchall()
    conn.close()

    existing_texts = [f"{row[0]} {' '.join(json.loads(row[1]))}" for row in existing_rows if row[1]]
    existing_embeddings = embedder.encode(existing_texts, convert_to_tensor=True) if existing_texts else None

    results = []
    threshold = 0.90  # similarity threshold for duplicate detection

    for uc in filtered_use_cases:
        if isinstance(uc, dict):  # skip error blocks
            results.append(uc)
            continue

        uc_emb = compute_usecase_embedding(uc)
        is_duplicate = False

        if existing_embeddings is not None:
            cos_sim = util.cos_sim(uc_emb, existing_embeddings)
            max_sim = float(torch.max(cos_sim))
            if max_sim >= threshold:
                is_duplicate = True

        if not is_duplicate:
            # Store in DB
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("""
                INSERT INTO use_cases 
                (title, preconditions, main_flow, sub_flows, alternate_flows, outcomes, stakeholders)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                uc.title,
                json.dumps(uc.preconditions),
                json.dumps(uc.main_flow),
                json.dumps(uc.sub_flows),
                json.dumps(uc.alternate_flows),
                json.dumps(uc.outcomes),
                json.dumps(uc.stakeholders)
            ))
            conn.commit()
            conn.close()
            results.append({"status": "stored", "title": uc.title})
        else:
            results.append({"status": "duplicate_skipped", "title": uc.title})

    return {"message": "Processed all chunks with RAG", "results": results}





