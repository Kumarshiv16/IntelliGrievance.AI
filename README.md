# 🛡️ IntelliGrievance AI – Enterprise Student Grievance Redressal System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.139.2-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12%20%7C%203.14-3776AB.svg?style=flat&logo=python)](https://python.org)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.8.0-F7931E.svg?style=flat&logo=scikitlearn)](https://scikit-learn.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg?style=flat&logo=postgresql)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An intelligent, explainable, natural language processing (NLP) grievance triage and routing platform tailored for modern universities. Automatically classifies unstructured student complaints across **12 institutional categories**, calculates **continuous severity scores (0–100)** and discrete urgency tiers (**Critical, High, Medium, Low**), enforces **deterministic safety overrides** for life-safety emergencies, routes complaints through multi-tier departmental escalation hierarchies, and clusters potential duplicate submissions using cosine similarity.

---

## 🌟 Key Architectural Features

1. **Dual NLP Classification Pipelines**:
   - **Category Classifier**: Evaluated across Multinomial Naive Bayes, Logistic Regression, Linear SVM, and Random Forest on 6,000 stratified samples. Multinomial Naive Bayes was selected for deployment ($100.00\%$ Macro F1-score on held-out test split).
   - **Severity & Urgency Predictor**: Balanced class-weighted Calibrated Logistic Regression ($96.42\%$ accuracy, $0.9644$ Macro F1).
2. **Deterministic Safety Safeguards**:
   - Algorithmic override prevents automated downgrade of urgent hazards (ragging, assault, fire, suicide, electrical shock). Forces 4-hour critical SLA turnaround.
3. **Explainable AI (XAI)**:
   - Decomposes predictions into token feature attribution and urgency drivers so students and administrators see *why* a ticket was categorized and prioritized.
4. **Semantic Duplicate Detection**:
   - Sublinear TF-IDF cosine similarity clusters related open complaints across campus residential blocks and departments.
5. **Role-Based Workspaces**:
   - **Student Portal**: Natural language submission, live AI routing preview, and real-time status tracking.
   - **Executive Admin Dashboard**: Cross-departmental workload analysis, 14-day trends, spatial hotspots, and recurring bigram discovery.
   - **Department Queue Workspace**: Department head investigations, internal remarks, and resolution lifecycle tracking.

---

## 🏗️ Project Structure

```
grievance-ai/
│
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/     # REST Endpoints (auth, grievances, ai, admin)
│   │   ├── core/                 # Config, Database Engine, Security (PBKDF2/JWT)
│   │   ├── models/               # SQLAlchemy ORM Models (Users, Grievances, etc.)
│   │   ├── schemas/              # Pydantic v2 Request/Response validation
│   │   ├── services/             # Database Seeder & Business Services
│   │   └── ml/                   # ML inference engines (Category, Severity, XAI, Routing)
│   ├── tests/                    # Automated Pytest suite (100% pass rate)
│   └── main.py                   # FastAPI Application Entrypoint
│
├── ml/
│   ├── data/                     # 6,000 sample stratified dataset
│   ├── preprocessing/            # Negation-preserving text cleaners & generator
│   ├── training/                 # Multi-model benchmarking script
│   ├── models/                   # Serialized production .joblib pipelines
│   └── reports/                  # Model evaluation reports (JSON & CSV)
│
├── frontend/
│   └── index.html                # Single-Page Application (Tailwind + Lucide + Chart.js)
│
├── scripts/
│   └── generate_pdf_report.py    # Report compiler
│
├── PROJECT_REPORT.md             # Complete Academic Capstone Report
├── PROJECT_REPORT.pdf            # PDF Academic Report (9 pages)
├── PROJECT_REPORT.docx           # Word Document Report
├── docker-compose.yml            # Multi-container Docker deployment
├── Dockerfile.backend            # Production backend Docker container
├── requirements.txt              # Python dependencies
└── README.md
```

---

## 🚀 Quickstart & Local Execution

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.12 and 3.14)
- Pip

### 2. Setup Virtual Environment & Install Dependencies
```bash
git clone https://github.com/your-username/intelligrievance-ai.git
cd grievance-ai

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Launch the Backend Server
```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
- **Web Application Portal**: Open [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger API Docs**: Open [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc API Documentation**: Open [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🔑 Demo Login Credentials

The system automatically initializes and seeds demo accounts on first launch:

| Role | Email Address | Password | Permissions |
|---|---|---|---|
| **System Administrator** | `admin@university.edu` | `AdminPassword123!` | Full analytics, SLA management, all tickets |
| **Department Head (Warden)** | `warden.head@university.edu` | `DeptPassword123!` | Hostel department ticket queue & resolution |
| **Department Head (COE)** | `coe.head@university.edu` | `DeptPassword123!` | Examination cell ticket queue & resolution |
| **Student (Aarav Sharma)** | `student@university.edu` | `StudentPassword123!` | File complaints, preview AI, view personal history |

---

## 🧪 Running Automated Tests

Run the full automated test suite covering ML inference, security hashing, JWT validation, and database ORM transactions:

```bash
python -m pytest backend/tests/test_suite.py -v
```

---

## 📊 Model Evaluation Summary

From the held-out test evaluation (`ml/reports/model_evaluation_report.json`):

| Task | Model Architecture | Metric | Result |
|---|---|---|---|
| **12-Class Categorization** | Multinomial Naive Bayes (alpha=0.1) | Accuracy / Macro F1 | **100.00% / 1.0000** |
| **4-Tier Priority Prediction** | Calibrated Logistic Regression (Class-Weighted) | Accuracy / Macro F1 | **96.42% / 0.9644** |
| **Safety Safeguard Override** | Heuristic Safety Interceptor | Emergency Hazard Recall | **100.00%** |
| **Inference Latency** | Optimized TF-IDF Pipelines | Average Inference Time | **< 3 milliseconds** |

---

## 📑 Academic Documentation

Complete capstone project documentation is available:
- **Markdown Report**: [PROJECT_REPORT.md](file:///c:/Users/dell/Downloads/grievance-ai/PROJECT_REPORT.md)
- **PDF Report**: [PROJECT_REPORT.pdf](file:///c:/Users/dell/Downloads/grievance-ai/PROJECT_REPORT.pdf)
- **Word Document**: [PROJECT_REPORT.docx](file:///c:/Users/dell/Downloads/grievance-ai/PROJECT_REPORT.docx)
