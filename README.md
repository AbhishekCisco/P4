# Employee Service Architecture Learning Project

## Overview

This repository contains two beginner-friendly Python examples for learning how applications expose and organize employee-management functionality:

1. **`employee_app/`** is a complete REST API that uses FastAPI, SQLAlchemy, SQLite, Pydantic, and a layered architecture.
2. **`SOA_Employee_Management/`** is a service-oriented architecture exercise that splits employee registration, department lookup, payroll calculation, and notifications among four independent FastAPI services.

The examples reinforce concepts that may be introduced in a day's learning material: API design, request validation, database operations, dependency injection, exceptions, inter-service HTTP requests, and separation of responsibilities. They are learning projects rather than production-ready employee systems.

Read the README inside the project you want to study:

- [employee_app/README.md](employee_app/README.md) for the layered, database-backed API
- [SOA_Employee_Management/README.md](SOA_Employee_Management/README.md) for the service-oriented architecture exercise

## Learning Objectives

After studying both folders, a learner should be able to:

- Explain the difference between a single application and several communicating services.
- Start and use FastAPI applications and interactive OpenAPI documentation.
- Validate incoming request data before it reaches application logic.
- Separate HTTP routing, business rules, database models, and database access.
- Perform SQLite CRUD operations with SQLAlchemy.
- Call one HTTP service from another with the `requests` library.
- Return appropriate HTTP success and error responses.
- Identify the persistence, security, and reliability limitations in a learning implementation.

## Topics Covered

### REST APIs

The examples demonstrate REST-style endpoints for creating, reading, updating, and deleting employees. FastAPI turns Python functions into HTTP endpoints and exposes interactive Swagger documentation.

### FastAPI and request handling

FastAPI reads values from the URL and JSON request body, converts them to Python types, and builds JSON responses. Pydantic models validate request fields and document the required fields and types.

### Layered architecture

The `employee_app` example separates responsibility among routers, services, repositories, database setup, and models. A router handles HTTP concerns, a service applies business rules, and a repository performs database queries.

### Service-oriented architecture

The SOA example divides functionality among independent Department, Employee, Payroll, and Notification services. The Employee Service validates a department through the Department Service and attempts to notify the employee through the Notification Service.

### SQLAlchemy and SQLite

`employee_app` uses SQLAlchemy for table models and queries, while SQLite stores records in `employees.db`. SQLAlchemy translates Python operations into database commands and does not require raw SQL for the operations in this project.

### HTTP communication between services

The SOA Employee Service uses `requests.get()` and `requests.post()` to communicate with other services. A request timeout prevents one call from waiting indefinitely.

### Validation and exception handling

Pydantic validates fields such as email addresses and positive salaries. Application code raises `HTTPException` or `ValueError` responses for missing records, duplicate email addresses, invalid salary values, unavailable services, and failed downstream requests.

### In-memory versus persistent storage

The SOA example keeps employee and department data in Python memory, so restarting a service clears employee registrations. The layered application persists employees in SQLite and keeps them after an application restart.

## Project Structure

```text
phase4/
├── README.md
├── employee_app/
│   ├── README.md
│   ├── employees.db
│   ├── main.py
│   ├── requirements.txt
│   ├── database/
│   │   └── connection.py
│   ├── models/
│   │   └── employee.py
│   ├── repositories/
│   │   └── employee_repository.py
│   ├── routers/
│   │   └── employee_router.py
│   └── services/
│       └── employee_service.py
└── SOA_Employee_Management/
    ├── README.md
    ├── requirements.txt
    ├── department_service/
    │   └── main.py
    ├── employee_service/
    │   └── main.py
    ├── notification_service/
    │   └── main.py
    └── payroll_service/
        └── main.py
```

## Quick Setup

Both projects use Python. The following commands assume Linux or macOS and a terminal opened in `/home/abrajpoo615/Desktop/phase4`.

### Start the database-backed employee API

```bash
cd employee_app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

### Start the SOA services

In one terminal, create and activate an environment:

```bash
cd SOA_Employee_Management
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Open four terminals using the same activated environment and run:

```bash
# Terminal 1
uvicorn department_service.main:app --port 8002 --reload

# Terminal 2
uvicorn employee_service.main:app --port 8001 --reload

# Terminal 3
uvicorn payroll_service.main:app --port 8003 --reload

# Terminal 4
uvicorn notification_service.main:app --port 8004 --reload
```

Use `http://127.0.0.1:8001/docs` for the main Employee Service. The Department, Payroll, and Notification services also have Swagger documentation at ports `8002`, `8003`, and `8004`.

On Windows PowerShell, activate an environment with:

```powershell
.\venv\Scripts\Activate.ps1
```

## Libraries and Tools

| Library or tool | Used for | Why it is used |
|---|---|---|
| Python | Application language | Provides the functions, classes, dictionaries, and exception handling used by both examples |
| FastAPI | REST framework | Converts Python functions into HTTP endpoints and creates interactive API documentation |
| Uvicorn | ASGI server | Runs FastAPI applications locally |
| Pydantic | Request and response validation | Checks JSON data types and email formats and separates API input/output schemas |
| `email-validator` | Email validation | Provides the email-address validation used by Pydantic's `EmailStr` |
| SQLAlchemy | Database mapping and queries | Maps Python `Employee` objects to a SQLite table and executes CRUD operations |
| SQLite | Database storage | Provides file-based, local storage for `employee_app` without an external database server |
| `requests` | Cross-service HTTP calls | Sends GET and POST requests from the SOA Employee Service to other services |

## Current Limitations and Errors

No authentication or authorization is implemented. Anyone who can reach the APIs may create, view, update, or delete employee data.

The SOA services do not use a shared database or persistent employee storage. Employees are stored in a Python list and disappear when the Employee Service restarts. Departments are a fixed dictionary: departments `101`, `102`, and `103` represent IT, HR, and Finance.

The Notification Service is simulated: it prints the employee name, email, and message to its terminal instead of sending a real email.

The SOA Employee Service has a resilience boundary: department lookup failure returns `502 Bad Gateway`, while notification failure does not undo employee registration and is returned with `status: "FAILED"`.

The example does not include Docker, a reverse proxy, service discovery, retries, circuit breakers, distributed tracing, migrations, or automated tests. It also does not use centralized logging or configuration.

The database example checks that salaries are greater than zero and emails are unique. It does not impose a maximum salary, verify department names, enforce authentication, or implement pagination.

## What to Study Next

After understanding the basic flow, study database migrations, authentication and authorization, automated API tests, logging, environment-based configuration, pagination, and asynchronous HTTP calls. Then add Docker, a reverse proxy, service discovery, or a message broker only after being comfortable with the simple communication in this repository.
