# Employee Management API

## Overview

`employee_app` is a database-backed REST API for managing employee records. It uses FastAPI for the HTTP interface, SQLAlchemy for database operations, Pydantic for request validation, and SQLite for local storage.

The project demonstrates a layered architecture: the API router receives HTTP requests, the service applies business rules, the repository changes the database, and the database models describe the employee table and API schemas.

This project fits as a practical example of CRUD—Create, Read, Update, and Delete—and of dividing one application into maintainable layers.

## Learning Objectives

After studying this folder, a learner should be able to:

- Start a FastAPI application and open Swagger documentation.
- Perform create, read, update, and delete operations through HTTP.
- Explain why routes, services, repositories, models, and database setup are separated.
- Use SQLAlchemy sessions and SQLite to persist Python objects.
- Validate JSON request data and distinguish API schemas from database models.
- Translate application exceptions into useful HTTP status codes.

## Topics Covered

### FastAPI REST routing

`main.py` creates the FastAPI application and includes a router at `/employees`. The router defines POST, GET, PUT, and DELETE endpoints, and FastAPI returns JSON responses.

### Pydantic data validation

`EmployeeCreate`, `EmployeeUpdate`, and `EmployeeResponse` in `models/employee.py` describe accepted and returned data. Pydantic checks types and, through `EmailStr`, validates email addresses. `salary` is a float but is also checked by the service to ensure it is greater than zero.

### SQLAlchemy data modeling

The `Employee` class maps to the `employees` SQLite table. Fields include an integer ID, a required name and department, a unique indexed email, and a required float salary.

### Database sessions

`database/connection.py` creates the SQLite engine and a SQLAlchemy session factory. `get_db()` creates a session for one request and closes it after the request finishes.

### Repository pattern

`EmployeeRepository` contains database operations. It adds and commits records, queries all or individual employees, updates submitted fields, and deletes records.

### Service layer and business rules

`EmployeeService` applies rules before or after repository operations. It rejects salaries less than or equal to zero, converts a missing employee into a meaningful error, and converts duplicate-email database failures into validation errors.

### CRUD and HTTP exceptions

The router maps application behavior to HTTP responses. Creation returns `201`, missing employees return `404`, invalid salaries and duplicate emails return `400`, and successful deletes return a JSON success message.

### Partial updates

An update uses `EmployeeUpdate.model_dump(exclude_unset=True)`, so a PUT request changes only fields included by the caller. For example, sending only `department` leaves name, email, and salary unchanged.

## Project Structure

```text
employee_app/
├── employees.db
├── main.py
├── requirements.txt
├── database/
│   └── connection.py
├── models/
│   └── employee.py
├── repositories/
│   └── employee_repository.py
├── routers/
│   └── employee_router.py
└── services/
    └── employee_service.py
```

## Important Files

### `main.py`

Creates the FastAPI application, gives it a title and description, creates database tables with `Base.metadata.create_all(bind=engine)`, and includes the employee router. `GET /` returns a welcome message.

### `database/connection.py`

Defines `sqlite:///./employees.db`, creates the SQLAlchemy engine, and sets `Base` and `SessionLocal`. `get_db()` supplies a database session to each endpoint and closes it afterward. `check_same_thread=False` is needed because SQLite may be used from FastAPI worker threads.

### `models/employee.py`

Defines both database and API models:

- `Employee` is the SQLAlchemy table model.
- `EmployeeCreate` describes required create requests.
- `EmployeeUpdate` makes every field optional for partial updates.
- `EmployeeResponse` describes returned employee data.

`ConfigDict(from_attributes=True)` allows a SQLAlchemy object to be converted into a Pydantic response model.

### `repositories/employee_repository.py`

Performs database work:

- creates and commits an employee
- retrieves all employees
- retrieves an employee by ID
- updates only submitted fields
- deletes an employee

### `services/employee_service.py`

Enforces application rules and translates SQLAlchemy's `IntegrityError` into a readable duplicate-email error. It also locates employees and raises `ValueError` when required records do not exist.

### `routers/employee_router.py`

Defines the `/employees` endpoints and translates `ValueError` into HTTP responses. The dependency `Depends(get_db)` gives each route a database session.

### `employees.db`

The SQLite database file that stores the `employees` table. It persists records between application restarts.

### `requirements.txt`

Lists `fastapi`, `uvicorn`, `sqlalchemy`, and `email-validator`.

## How the Files Work Together

1. `main.py` creates the application and registers `employee_router.py`.
2. A request arrives at an endpoint in `employee_router.py`.
3. FastAPI validates JSON using a Pydantic model from `models/employee.py`.
4. `Depends(get_db)` supplies a SQLAlchemy session from `database/connection.py`.
5. The router calls `EmployeeService`.
6. `EmployeeService` validates business rules and calls `EmployeeRepository`.
7. The repository creates, reads, updates, or deletes a SQLAlchemy `Employee` model.
8. SQLAlchemy commits the change to `employees.db`.
9. FastAPI serializes the returned employee into `EmployeeResponse`.

## Libraries and Tools

| Library or tool | Used for | Why it is used |
|---|---|---|
| FastAPI | REST API framework | Defines endpoints, dependency injection, validation, documentation, and JSON responses |
| Uvicorn | ASGI server | Runs the FastAPI application |
| Pydantic | Data schemas | Validates request and response fields and email addresses |
| `email-validator` | Email validation | Supplies Pydantic's `EmailStr` with real email syntax validation |
| SQLAlchemy | ORM and database API | Maps Python classes to database tables and records; prevents every simple operation from requiring raw SQL |
| SQLite | Local database | Stores data in `employees.db` without an external database server |

## Setup

Run these commands from the repository root:

```bash
cd employee_app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

On Windows PowerShell:

```powershell
cd employee_app
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

The default server address is `http://127.0.0.1:8000`.

Open `http://127.0.0.1:8000/docs` for Swagger UI. Swagger UI lets a learner execute requests without writing a separate client.

## API Behavior and Example Requests

### Welcome endpoint

`GET /` returns:

```json
{"message": "Welcome to Employee Management API"}
```

### Create an employee

`POST /employees/`

```json
{
  "name": "Abhishek",
  "email": "abhishek@example.com",
  "department": "IT",
  "salary": 50000
}
```

A successful request returns `201` and the created employee, including its database ID.

### List employees

`GET /employees/` returns all stored employees.

### Retrieve one employee

`GET /employees/{employee_id}` returns the matching employee or `404` with `Employee not found`.

### Update an employee

`PUT /employees/{employee_id}`

For example:

```json
{"department": "Finance"}
```

Only the supplied fields are changed. A salary less than or equal to zero returns `400`; an unknown employee returns `404`.

### Delete an employee

`DELETE /employees/{employee_id}` returns:

```json
{"message": "Employee deleted successfully"}
```

An unknown employee returns `404`.

## Errors and Limitations

- No authentication or authorization is included.
- An email must be valid and unique.
- Salary must be greater than zero.
- The update endpoint uses PUT but supports partial data; a learner should understand that only supplied fields are changed.
- Department is stored as a string and is not validated against a department table.
- The database is local and not intended for production-scale concurrent use.
- No migrations, automated tests, pagination, logging, or environment configuration are included.
- SQLite table creation occurs automatically when `main.py` starts.

## What to Study Next

Study database migrations and how they manage schema changes. Next, add automated tests for the router, service, and repository; authentication and authorization; pagination and sorting; and environment-based database configuration.

For the same employee domain on a smaller service-oriented model, continue with [SOA_Employee_Management/README.md](../SOA_Employee_Management/README.md).
