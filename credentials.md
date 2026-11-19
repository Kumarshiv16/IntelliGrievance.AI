# 🔑 IntelliGrievance AI – System Credentials & Access Directory

This document contains all pre-configured demo user accounts, administrative credentials, API access tokens, and role-based permissions for **IntelliGrievance AI**.

All accounts are pre-seeded automatically into the local database upon initial launch.

---

## 👥 Pre-Configured Demo Accounts

| Role | Name & Title | Email Address | Password | Department / Scope |
|---|---|---|---|---|
| **System Administrator** | Dr. Sarah Jenkins (Registrar) | `admin@university.edu` | `AdminPassword123!` | Global (All Departments, SLAs, Analytics, Audit Logs) |
| **Department Head** | Col. V. Sharma (Chief Warden) | `warden.head@university.edu` | `DeptPassword123!` | Hostel & Residential Administration (`HOSTEL`) |
| **Department Head** | Prof. R. Narayanan (Controller of Exams) | `coe.head@university.edu` | `DeptPassword123!` | Examination & Evaluation Cell (`COE`) |
| **Department Head** | Dr. Meenakshi Sundaram (Dean Academics) | `acad.head@university.edu` | `DeptPassword123!` | Academic Affairs & Curriculum (`ACAD`) |
| **Student** | Aarav Sharma | `student@university.edu` | `StudentPassword123!` | Roll No: `22CSE104` (BTech 3rd Year CSE) |
| **Student** | Priya Patel | `priya.patel@university.edu` | `StudentPassword123!` | Roll No: `22AIML045` (BTech 3rd Year AIML) |
| **Student** | Rohit Verma | `rohit.verma@university.edu` | `StudentPassword123!` | Roll No: `21ECE088` (BTech 4th Year ECE) |

---

## 🛡️ Role-Based Access Control (RBAC) Matrix

| Feature / Workspace | Student | Department Head | System Administrator |
|---|:---:|:---:|:---:|
| **Live NLP Playground & Inference Preview** | ✅ | ✅ | ✅ |
| **File New Grievance** | ✅ | ❌ | ❌ |
| **View Personal Grievance History & SLA** | ✅ | ❌ | ❌ |
| **View Assigned Department Queue** | ❌ | ✅ | ✅ |
| **Update Grievance Status & Resolution Remarks** | ❌ | ✅ | ✅ |
| **Reassign Departments & Escalations** | ❌ | ❌ | ✅ |
| **Cross-Departmental SLA Analytics & Charts** | ❌ | ❌ | ✅ |
| **Spatial Hotspots & N-gram Trend Mining** | ❌ | ❌ | ✅ |
| **Inspect System & User Audit Logs** | ❌ | ❌ | ✅ |

---

## 🔐 Database & Environment Credentials

### Local Development (Default SQLite)
- **Path:** `backend/intelligrievance.db`
- **Zero Config:** Automatically created on first launch with no external database server required.

### Production Environment (PostgreSQL)
Defined in `docker-compose.yml` and `.env`:
- **Host:** `localhost` (or `db` inside Docker network)
- **Port:** `5432`
- **Database:** `intelligrievance_db`
- **Username:** `intelligrievance_user`
- **Password:** `intelligrievance_pass`
- **Database URL:** `postgresql://intelligrievance_user:intelligrievance_pass@localhost:5432/intelligrievance_db`

### JWT Token Configuration
- **Algorithm:** `HS256` (HMAC-SHA256)
- **Secret Key:** Configured in `backend/app/core/config.py` (Override via `SECRET_KEY` in `.env`)
- **Token Validity:** 1440 minutes (24 hours)

---

## 💡 Quick Login via the Web Interface

1. Open **[http://localhost:8000](http://localhost:8000)** in your browser.
2. Click **"Sign In"** in the top navigation bar.
3. Use the **Quick Demo Login Shortcuts** at the bottom of the modal to log in with one click as **Administrator**, **Dept Head**, or **Student**.
