# 💡 ReqEngine: Intelligent Requirements Engineering Tool

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API_Framework-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React_19-61DAFB.svg?logo=react&logoColor=white)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Build_Tool-Vite-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev/)
[![TailwindCSS](https://img.shields.io/badge/Styling-TailwindCSS-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Transformers](https://img.shields.io/badge/AI-Transformers-FF6F00.svg?logo=huggingface&logoColor=white)](https://huggingface.co/transformers/)
[![ChromaDB](https://img.shields.io/badge/Vector_DB-ChromaDB-FF6B6B.svg)](https://www.trychroma.com/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXX)

## Code Quality & Testing

[![ESLint](https://img.shields.io/badge/Code_Style-ESLint-4B32C3.svg?logo=eslint&logoColor=white)](https://eslint.org/)
[![Pytest](https://img.shields.io/badge/Testing-Pytest-0A9EDC.svg?logo=pytest&logoColor=white)](https://pytest.org/)
[![Vitest](https://img.shields.io/badge/Frontend_Testing-Vitest-6E9F18.svg?logo=vitest&logoColor=white)](https://vitest.dev/)
[![Coverage](https://img.shields.io/badge/Coverage-pytest--cov-brightgreen.svg)](https://pytest-cov.readthedocs.io/)

---

## 🌟 Project Overview

**ReqEngine** is an intelligent requirements engineering tool built on **FastAPI** that uses a fine-tuned **Large Language Model (LLaMA 3.2 3B Instruct)** to automatically transform unstructured textual requirements into structured, high-quality **Use Case Specifications**. It is engineered for efficiency, accuracy, and reliability across documents of any size.

---

## 🏗️ Project Structure

### Backend (FastAPI + Python)
```
backend/
├── main.py                    # FastAPI application and API endpoints
├── db.py                      # SQLite database operations
├── document_parser.py         # Multi-format document processing
├── chunking_strategy.py       # Intelligent text chunking
├── rag_utils.py              # RAG and semantic search utilities
├── use_case_enrichment.py    # LLM-based content enhancement
├── use_case_validator.py     # Quality validation logic
├── export_utils.py           # Multi-format export functionality
└── requirements.txt          # Python dependencies
```

### Frontend (React + Vite)
```
frontend/
├── src/
│   ├── components/           # Reusable UI components
│   ├── pages/               # Application pages/views
│   ├── api/                 # API client configuration
│   ├── store/               # Zustand state management
│   └── utils/               # Utility functions
├── package.json             # Node.js dependencies
├── vite.config.js          # Vite build configuration
├── tailwind.config.cjs     # TailwindCSS styling
└── eslint.config.js        # ESLint code style rules
```

---

## ✨ Key Features

### 🧠 Intelligent Requirements Processing
- **Smart Use Case Extraction**: Automatically analyzes input text to estimate the number of distinct use cases
- **Dynamic Token Budgeting**: Adapts LLM response length based on content complexity
- **Semantic Duplicate Detection**: Uses Sentence Transformers to identify and prevent duplicate requirements
- **Multi-format Document Support**: Processes PDF, DOCX, TXT, and Markdown files

### 📊 Advanced Analytics
- **Quality Validation**: Automatically validates structure and completeness of extracted use cases
- **Interactive Refinement**: Allows users to iteratively improve specific use case components
- **Natural Language Queries**: RAG-enabled querying against extracted requirements
- **Session Management**: Persistent storage of project context and conversation history

### 🚀 Export Capabilities
- **Microsoft Word (.docx)**: Professional specification documents
- **Markdown (.md)**: Documentation-ready format
- **PlantUML**: Use case diagram generation
- **JSON**: Structured data for programmatic access
- **JIRA**: Direct integration format
- **HTML**: Web-ready presentations

---

## 💻 Installation and Setup

### Prerequisites

1. **Python 3.9+**
2. A system with a **GPU** supporting CUDA is **highly recommended** for running the LLaMA 3 3B model, even with quantization.

### Setup Steps

1. **Clone the Repository (Assumed)**
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: This includes `torch`, `transformers` with `bitsandbytes`, `fastapi`, `uvicorn`, `python-docx`, `PyPDF2`, and `sentence-transformers`.)*
3. **Set Hugging Face Token:** The LLaMA 3 model is gated, requiring a valid token as an environment variable:
   ```bash
   export HF_TOKEN="your_huggingface_token"
   ```
4. **Run the ReqEngine API:**
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
```

---

## 🧪 Testing

### Backend Testing (Python/Pytest)

```bash
cd backend
pytest                          # Run all tests
pytest --cov=. --cov-report=html  # Run with coverage
pytest -v tests/test_main.py    # Run specific test file
```

**Test Statistics:**
- **Total Tests**: 45+ comprehensive test cases
- **Coverage Target**: 80%+ code coverage
- **Test Categories**: Unit, Integration, and API tests
- **Test Files**: 8 test modules covering all major components

**Test Coverage Includes:**
- API endpoint testing
- Database operations
- Document parsing functionality
- Use case validation logic
- Integration tests

### Frontend Testing (Vitest)

```bash
cd frontend
npm test                        # Run all tests
npm run test:coverage          # Run with coverage
npm run test:ui               # Run with UI interface
```

**Test Statistics:**
- **Total Tests**: 35+ component and integration tests
- **Coverage Target**: 80%+ code coverage
- **Test Categories**: Component, Integration, and User interaction tests
- **Test Files**: 15+ test files across components and pages

**Test Coverage Includes:**
- Component unit tests
- API client testing
- State management testing
- User interaction testing

---

## 📡 API Integration

### Core Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/parse_use_case_rag/` | POST | Extract use cases from raw text |
| `/parse_use_case_document/` | POST | Extract use cases from uploaded file |
| `/session/create` | POST | Create new requirements session |
| `/session/update` | POST | Update session context |
| `/sessions/` | GET | List all sessions |
| `/session/{id}/history` | GET | Get session conversation history |
| `/session/{id}/export` | GET | Export session data |
| `/use-case/refine` | POST | Refine specific use case |
| `/query` | POST | Natural language query against requirements |

### Usage Examples

#### Text-based Extraction
```python
import requests

response = requests.post('http://localhost:8000/parse_use_case_rag/', json={
    "raw_text": "Users must be able to login and search for products",
    "project_context": "E-commerce Platform",
    "domain": "Retail"
})
```

#### Document Upload
```python
files = {'file': open('requirements.pdf', 'rb')}
data = {
    'project_context': 'Banking System',
    'domain': 'Financial Services'
}
response = requests.post('http://localhost:8000/parse_use_case_document/', 
                        files=files, data=data)
```

---

##  Documentation

### 📋 Quick Reference
- **[Setup Guide](docs/SETUP.md)** - Quick setup instructions for development
- **[Installation Guide](docs/INSTALL.md)** - Comprehensive installation and configuration
- **[API Reference](docs/API.md)** - Complete REST API documentation with examples

### 🛠️ Development Resources
- **[Contributing Guidelines](docs/CONTRIBUTING.md)** - Development workflow and coding standards
- **[Code of Conduct](docs/CODE-OF-CONDUCT.md)** - Community guidelines and behavior standards
- **[Changelog](docs/CHANGELOG.md)** - Version history and release notes

### 🏗️ Architecture Documentation
- **[Backend README](backend/README.md)** - FastAPI backend architecture and APIs
- **[Frontend README](frontend/README.md)** - React frontend components and structure

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes and add tests
4. Run quality checks:
   ```bash
   # Backend
   cd backend && pytest --cov=.
   
   # Frontend  
   cd frontend && npm run lint && npm test
   ```
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.