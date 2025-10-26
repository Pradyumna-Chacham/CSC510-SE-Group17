import os
from typing import List
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer

# --- Semantic chunking ---
def semantic_chunk(text: str, chunk_size: int = 30, overlap: int = 10) -> List[str]:
    """
    Split text into overlapping semantic chunks (by sentences).
    
    Args:
        text: The raw document text.
        chunk_size: Number of sentences per chunk.
        overlap: Number of sentences to overlap between chunks.

    Returns:
        List of text chunks.
    """
    # Split text into sentences
    sentences = [s.strip() for s in text.split(". ") if s.strip()]
    
    chunks = []
    start = 0
    step = chunk_size - overlap
    total_sentences = len(sentences)
    
    while start < total_sentences:
        end = min(start + chunk_size, total_sentences)
        chunk = ". ".join(sentences[start:end])
        if chunk:
            chunks.append(chunk)
        start += step
    
    return chunks


# --- Initialize vector DB ---
def init_vector_db():
    client = chromadb.Client()
    collection = client.get_or_create_collection(
        name="usecase_chunks",
        embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
    )
    return collection

# --- Add chunks to vector DB ---
def add_chunks_to_db(collection, chunks: List[str]):
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    collection.add(ids=ids, documents=chunks)

# --- Retrieve relevant chunks ---
def retrieve_chunks(collection, query: str, n_results: int = 5) -> List[str]:
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results['documents'][0]
