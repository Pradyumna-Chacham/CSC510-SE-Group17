## 💡 ReqEngine: Intelligent Requirements Engineering Tool

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API_Framework-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LLaMA 3](https://img.shields.io/badge/Core_Model-LLaMA%203.2%203B%20Instruct-FF69B4.svg?logo=meta&logoColor=white)](https://llama.meta.com/)
[![Quantization](https://img.shields.io/badge/Performance-4--bit%20Quantized-purple.svg)](https://github.com/TimDettmers/bitsandbytes)
[![SQLite](https://img.shields.io/badge/Data_Persistence-SQLite-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/index.html)
[![Sentence Transformers](https://img.shields.io/badge/Duplicate_Detection-Sentence%20Transformers-orange.svg)](https://www.sbert.net/)

**ReqEngine** is an intelligent requirements engineering tool built on **FastAPI** that uses a fine-tuned **Large Language Model (LLaMA 3.2 3B Instruct)** to automatically transform unstructured textual requirements into structured, high-quality **Use Case Specifications**. It is engineered for efficiency, accuracy, and reliability across documents of any size.

---

## ✨ Core Innovations

### 🧠 Smart & Reliable Extraction (V4.0)
* **Intelligent Use Case Estimation:** ReqEngine automatically analyzes the input text (counting unique action verbs, actors, and structural elements) to **estimate the actual number of distinct use cases**. This prevents the LLM from hallucinating requirements due to fixed, hardcoded limits.
* **Dynamic Token Budgeting:** The LLM's response length is dynamically calculated based on the estimated use case count, ensuring **fast generation** for small inputs and adequate detail for complex ones.
* **Size-Adaptive Processing:** Automatically detects the size category of the input text and selects the optimal strategy:
    * **Batch/Single-Stage Extraction:** Used for small to medium inputs for speed.
    * **Intelligent Chunking:** Splits large documents (over 20,000 characters) into context-aware chunks for sequential processing and de-duplication.

### 📄 Document & Data Handling
* **Multi-Format Document Parsing:** Accepts and processes uploaded requirements documents in **PDF, DOCX, TXT, and Markdown (.md)** formats.
* **Semantic Duplicate Detection:** Uses **Sentence Transformers** to generate embeddings and compare use cases, ensuring that semantically similar, redundant requirements are not stored.
* **Quality Validation & Enrichment:** Automatically validates the structure and completeness of extracted use cases and uses the LLM to enrich sparse flow steps or missing details.
* **Persistent Session Management:** All extracted use cases, project context, and conversation history are stored in **SQLite** for continuity and easy retrieval.

---

## 🛠️ Key Functionality

### API Endpoints (as a Service)
| Endpoint | Description | Method |
| :--- | :--- | :--- |
| `/parse_use_case_rag/` | **Smart Extraction** from raw text input. | `POST` |
| `/parse_use_case_document/` | **Smart Extraction** from uploaded file (PDF, DOCX, etc.). | `POST` |
| `/session/create` | Starts a new requirements engineering session. | `POST` |
| `/use-case/refine` | Interactively refines a specific use case field (e.g., add more alternate flows). | `POST` |
| `/query` | **Natural Language Query** (RAG-lite) against extracted use cases. | `POST` |
| `/session/{session_id}/export/{format}` | Exports use cases to **DOCX**, **Markdown**, or other formats. | `GET` |
| `/sessions/` | Lists all active sessions with intelligent titles. | `GET` |

### Export Formats
ReqEngine supports comprehensive export for downstream tools:
* **Microsoft Word (.docx)**: Professional specification document.
* **Markdown (.md)**: Easy integration into documentation wikis.
* **PlantUML Code**: Generates the code for a Use Case Diagram.
* **Structured JSON**: For programmatic integration.
* **JIRA**: Converts to JIRA Issue JSON format.
* **HTML**: For web viewing.

---

## 💻 Installation and Setup

### Prerequisites

1.  **Python 3.9+**
2.  A system with a **GPU** supporting CUDA is **highly recommended** for running the LLaMA 3 3B model, even with quantization.

### Setup Steps

1.  **Clone the Repository (Assumed)**
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: This includes `torch`, `transformers` with `bitsandbytes`, `fastapi`, `uvicorn`, `python-docx`, `PyPDF2`, and `sentence-transformers`.)*
3.  **Set Hugging Face Token:** The LLaMA 3 model is gated, requiring a valid token as an environment variable:
    ```bash
    export HF_TOKEN="your_huggingface_token"
    ```
4.  **Run the ReqEngine API:**
    ```bash
    uvicorn main:app --reload
    ```

The service will be available at `http://127.0.0.1:8000`. Interact with the API documentation at `http://127.0.0.1:8000/docs`.

---

## 🔍 Structured Output Example

When processing a requirement like: "*The user must be able to securely login to their account and search for products using keywords. If an item is out of stock, the system must notify the user.*", ReqEngine separates the compound actions into distinct, structured use cases.

The JSON output will contain an array of objects structured as follows:

```json
[
  {
    "id": 1,
    "title": "User Logs In To System",
    "preconditions": [
      "User has valid credentials"
    ],
    "main_flow": [
      "User opens login screen",
      "User enters credentials",
      "System validates credentials",
      "System authenticates user"
    ],
    "sub_flows": [
      "User can reset password"
    ],
    "alternate_flows": [
      "If invalid credentials: System shows error message"
    ],
    "outcomes": [
      "User is logged in successfully"
    ],
    "stakeholders": [
      "User",
      "Authentication System"
    ]
  },
  {
    "id": 2,
    "title": "User Searches For Products",
    "preconditions": [
      "User is logged in",
      "Product catalog is available"
    ],
    "main_flow": [
      "User navigates to search bar",
      "User enters keywords",
      "System returns matching products"
    ],
    "sub_flows": [
      "User can filter and sort results"
    ],
    "alternate_flows": [
      "If no match: System displays 'No results found'",
      "If item out of stock: System notifies user"
    ],
    "outcomes": [
      "Relevant product list is displayed"
    ],
    "stakeholders": [
      "User",
      "Inventory System"
    ]
  }
]