# 🚀 IntelliGrievance AI – Complete Execution & Setup Guide

This step-by-step guide explains how to install, configure, execute, and verify **IntelliGrievance AI** across Windows, macOS, Linux, and Docker environments.

---

## 📋 System Prerequisites

Ensure you have the following installed on your machine:
- **Python:** Version 3.10, 3.11, 3.12, or 3.14 (Verified compatible).
- **Package Manager:** `pip` (bundled with Python).
- **Web Browser:** Any modern browser (Google Chrome, Microsoft Edge, Firefox, Brave, Safari).
- *(Optional)* **Docker & Docker Compose:** If running in a containerized environment.

Check your Python version:
```bash
python --version
# Output should be Python 3.10 or higher
```

---

## ⚡ Method 1: Local Setup (Recommended & Fastest)

### Step 1: Open Terminal / PowerShell
Navigate to the root directory of the project:
```bash
cd grievance-ai
```

### Step 2: Create and Activate a Virtual Environment
Isolating dependencies ensures a clean runtime environment:

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Python Packages
```bash
pip install -r requirements.txt
```
*(Dependencies installed: FastAPI, Uvicorn, Scikit-learn, SQLAlchemy, Pydantic, NumPy, Pandas, Pytest).*

### Step 4: Launch the Server
Run the FastAPI application via Uvicorn:
```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

You should see terminal output indicating that the database tables and demo seed records were initialized:
```
INFO:     Started server process
INFO:     Waiting for application startup.
Creating all database tables...
Database successfully seeded! 18 grievances loaded.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 🌐 Accessing the Application

Once the server is running, open your browser and navigate to:

| Destination | URL | Description |
|---|---|---|
| **Web Application Portal** | **[http://localhost:8000](http://localhost:8000)** | Full dashboard (NLP Playground, Student Portal, Admin Analytics, Dept Workspace) |
| **Interactive API Documentation** | **[http://localhost:8000/docs](http://localhost:8000/docs)** | Swagger UI to test and inspect all REST endpoints directly |
| **Alternative API Specification** | **[http://localhost:8000/redoc](http://localhost:8000/redoc)** | ReDoc clean technical documentation |
| **Health Check Endpoint** | **[http://localhost:8000/health](http://localhost:8000/health)** | Returns JSON service status |

---

## 🐳 Method 2: Running with Docker & Docker Compose

If you prefer to run the multi-tier containerized stack with **PostgreSQL**:

1. Ensure Docker Desktop is running.
2. Build and start all services:
   ```bash
   docker-compose up --build
   ```
3. Docker will automatically launch:
   - `intelligrievance_db`: PostgreSQL 15 on port `5432`
   - `intelligrievance_backend`: FastAPI app on port `8000`
4. Access the portal at `http://localhost:8000`.
5. To stop the containers:
   ```bash
   docker-compose down
   ```

---

## 🧪 How to Run Automated Verification Tests

A complete automated unit and integration test suite is included in `backend/tests/test_suite.py`.

Run the test suite from the root folder:
```bash
python -m pytest backend/tests/test_suite.py -v
```

Expected output:
```
============================= test session starts =============================
collected 8 items

backend\tests\test_suite.py::test_category_classification PASSED        [ 12%]
backend\tests\test_suite.py::test_hostel_category_and_safeguard PASSED  [ 25%]
backend\tests\test_suite.py::test_explainability_engine PASSED          [ 37%]
backend\tests\test_suite.py::test_department_routing PASSED             [ 50%]
backend\tests\test_suite.py::test_semantic_similarity_duplicates PASSED [ 62%]
backend\tests\test_suite.py::test_password_hashing PASSED               [ 75%]
backend\tests\test_suite.py::test_jwt_token_cycle PASSED                [ 87%]
backend\tests\test_suite.py::test_database_grievance_lifecycle PASSED  [100%]

======================== 8 passed in 2.50s ========================
```

---

## 🔄 Retraining Machine Learning Models (Optional)

If you modify or expand the grievance templates in `ml/preprocessing/generate_dataset.py`, you can regenerate the dataset and re-benchmark all models with two commands:

1. **Regenerate the dataset:**
   ```bash
   python ml/preprocessing/generate_dataset.py
   ```
2. **Train and compare all classifiers:**
   ```bash
   python ml/training/train_models.py
   ```
This updates the serialized models in `ml/models/` and refreshes `ml/reports/model_evaluation_report.json`.

---

## 🛠️ Common Troubleshooting

### 1. `Port 8000 is already in use`
Change the port flag when running Uvicorn:
```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8080 --reload
```
Then access the portal at `http://localhost:8080`.

### 2. `ModuleNotFoundError: No module named 'backend'`
Ensure you are running the commands from the root `grievance-ai` directory, or add current path to your `PYTHONPATH`:
```bash
# Windows PowerShell
$env:PYTHONPATH = (Get-Location).Path

# Linux / macOS
export PYTHONPATH=$(pwd)
```

### 3. Resetting the Database
If you wish to reset all tickets and seed data back to the clean initial state, simply delete the SQLite file and restart the server:
```powershell
Remove-Item backend/intelligrievance.db
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
