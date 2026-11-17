# TaskFlow – Role-Based Task Management System

A web-based task management application built with Python, FastAPI, PostgreSQL, and JavaScript. TaskFlow provides a centralized platform for managing employees, assigning tasks, tracking task progress, and monitoring working hours through three role-based dashboards.

## 1. Project Overview

TaskFlow is designed around three user roles:

- **Admin:** Manages Managers and monitors overall system activity.
- **Manager:** Manages employees, creates and assigns tasks, tracks task history, and monitors team working hours.
- **Employee:** Views assigned tasks, updates task status, and submits working-hour records.

The application implements Role-Based Access Control (RBAC) to ensure that users can access only the resources permitted for their roles.

## 2. Key Features

### Admin Module
- Admin authentication.
- Create and manage Managers.
- View all Managers.
- Edit Manager details.
- Activate and deactivate Manager accounts.
- View employee directory.
- View Manager details and their employees.
- Monitor overall dashboard statistics.

### Manager Module
- Manager authentication.
- Create and manage Employees.
- Edit Employee details.
- Activate and deactivate Employee accounts.
- View team members.
- Create and assign tasks.
- View assigned team tasks.
- Reassign tasks between team members.
- View task activity and reassignment history.
- Monitor employee time logs.

### Employee Module
- Employee authentication.
- Personal Employee Dashboard.
- View assigned tasks.
- View complete task details.
- Update task status:
  - Pending
  - In Progress
  - Completed
- Submit working hours.
- Add work descriptions and dates.
- View personal time-log history.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | REST API development |
| HTML5 | Frontend structure |
| CSS3 | Frontend styling |
| JavaScript | Frontend functionality and API integration |
| PostgreSQL | Relational database |
| Docker | Database containerization |
| SQLAlchemy | Object Relational Mapping (ORM) |
| Alembic | Database migrations |
| Pydantic | Data validation and serialization |
| JWT | Token-based authentication |
| Argon2 | Password hashing |
| Uvicorn | ASGI application server |
| Swagger UI | API documentation and testing |
| Git | Version control |

## 4. System Architecture

```text
                    TASKFLOW
                       |
              Frontend Application
              HTML + CSS + JavaScript
                       |
                  REST APIs
                    FastAPI
                       |
             Authentication & Security
              JWT + Argon2 + RBAC
                       |
                 SQLAlchemy ORM
                       |
                  PostgreSQL
                  (Docker)
```

## 5. Project Structure

```text
management_system/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   └── v1/
│   │   │       ├── router.py
│   │   │       └── endpoints/
│   │   │           ├── auth.py
│   │   │           ├── admin.py
│   │   │           ├── manager.py
│   │   │           └── employee.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── permissions.py
│   │   │   └── security.py
│   │   │
│   │   ├── database/
│   │   │   ├── base.py
│   │   │   └── connection.py
│   │   │
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── utils/
│   │   └── main.py
│   │
│   ├── migrations/
│   ├── .env.example
│   ├── alembic.ini
│   └── requirements.txt
│
├── frontend/
│   ├── admin/
│   ├── manager/
│   ├── employee/
│   ├── css/
│   ├── js/
│   ├── assets/
│   ├── index.html
│   └── login.html
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

## 6. Database Design

TaskFlow uses PostgreSQL with the following primary models:

### User
Stores account information for Admins, Managers, and Employees.

Important fields include:
- id
- name
- email
- password_hash
- role
- is_active
- manager_id

### Task
Stores task information and assignments.

Important fields include:
- id
- title
- description
- status
- priority
- created_by_id
- assigned_to_id
- due_date

### TaskHistory
Maintains a record of task activities and changes.

Important fields include:
- id
- task_id
- changed_by_id
- action
- old_status
- new_status
- old_assignee_id
- new_assignee_id
- remarks
- changed_at

### TimeLog
Stores employee working-hour records.

Important fields include:
- id
- task_id
- employee_id
- hours_worked
- work_date
- description

## 7. Authentication and Security

The application implements:

- JWT-based authentication.
- Argon2 password hashing.
- Role-based API authorization.
- Active-account verification.
- Server-side role validation during login.
- Manager team-level access restrictions.
- Employee task ownership restrictions.
- Protected API endpoints.

The backend verifies permissions rather than relying only on frontend role selection.

## 8. Installation and Setup

### Prerequisites

Install the following:

- Python 3.13 or compatible version.
- Docker Desktop.
- Git.
- Visual Studio Code.
- A modern web browser.

### Step 1: Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd management_system
```

### Step 2: Start PostgreSQL Using Docker

```bash
docker compose up -d
```

Check running containers:

```bash
docker ps
```

### Step 3: Create and Activate Virtual Environment

Windows PowerShell:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 4: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables

Configure the backend environment using the provided `.env.example` as a reference.

Create your local `.env` file and supply the database connection details, security settings, and other required configuration values.

Do not commit actual passwords, secret keys, or other sensitive credentials.

### Step 6: Apply Database Migrations

From the backend directory:

```bash
alembic upgrade head
```

### Step 7: Start FastAPI

```bash
uvicorn app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Swagger API Documentation:

```text
http://127.0.0.1:8000/docs
```

### Step 8: Start Frontend

Open the `frontend/login.html` file using the VS Code Live Server extension.

Example URL:

```text
http://127.0.0.1:5500/frontend/login.html
```

## 9. API Modules

The application exposes REST APIs under:

```text
/api/v1/
```

### Authentication
- POST `/auth/login`

### Admin
- GET `/admin/dashboard`
- GET `/admin/employees`
- GET `/admin/managers/{manager_id}`
- PATCH `/admin/managers/{manager_id}`

### Manager
- POST `/managers/`
- GET `/managers/`
- POST `/managers/employees`
- GET `/managers/employees`
- POST `/managers/tasks`
- GET `/managers/tasks`
- PATCH `/managers/tasks/{task_id}/reassign`
- GET `/managers/tasks/{task_id}/history`
- GET `/managers/time-logs`

### Employee
- GET `/employee/profile`
- GET `/employee/tasks`
- GET `/employee/tasks/{task_id}`
- PATCH `/employee/tasks/{task_id}/status`
- POST `/employee/tasks/{task_id}/time-logs`
- GET `/employee/time-logs`

For complete request and response schemas, use Swagger UI.

## 10. Testing

The project APIs have been tested using Swagger UI and the frontend has been manually validated.

Testing areas include:

- Login validation.
- Incorrect credentials.
- Role mismatch validation.
- Employee and Manager management.
- Task creation and assignment.
- Task reassignment.
- Task history.
- Employee task status updates.
- Working-hour submission.
- Role-based access restrictions.
- Frontend form validation.
- Dashboard data loading.

## 11. Future Enhancements

Potential future improvements include:

- Advanced dashboard analytics.
- Search, filtering, and pagination.
- Excel and PDF report exports.
- Enhanced reporting.
- Profile management.
- Automated testing with Pytest.

## 12. Author

**Project:** TaskFlow – Role-Based Task Management System

**Developer:** Pintu Sharma

**Backend:** Python, FastAPI, PostgreSQL

**Frontend:** HTML, CSS, JavaScript

**Version:** 1.0

---

*TaskFlow – Simplifying Employee Management, Task Assignment, and Work Tracking.*