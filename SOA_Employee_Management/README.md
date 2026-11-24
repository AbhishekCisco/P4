# SOA Employee Management

## Overview

`SOA_Employee_Management` is a service-oriented architecture exercise built with FastAPI. It demonstrates an employee registration workflow by dividing responsibilities among four independent services:

- Department Service
- Employee Service
- Payroll Service
- Notification Service

The project exists to teach learners how separate services communicate over HTTP, validate request data, own different responsibilities, and handle service failures. It is an in-memory exercise, so it is not a production employee system.

## Learning Objectives

After studying this folder, a learner should be able to:

- Explain the purpose of service-oriented architecture.
- Start and operate several FastAPI servers on different ports.
- Send HTTP requests between services.
- Validate data with Pydantic and `EmailStr`.
- Use timeouts and `raise_for_status()` for inter-service calls.
- Explain the difference between a successful operation and an available downstream notification.
- Recognize why in-memory storage and the absence of discovery or authentication are learning-project limitations.

## Topics Covered

### Service-oriented architecture

Each service owns a small area of responsibility. The Department Service provides department lookup, the Employee Service coordinates employee registration, the Payroll Service calculates salary components, and the Notification Service simulates sending a notification.

### REST APIs and multiple servers

FastAPI exposes endpoints from each service. Uvicorn runs every service on an independent local port.

### Pydantic request models

Pydantic verifies JSON bodies. `EmailStr` validates email addresses, and `Field(gt=0)` requires a basic salary greater than zero.

### HTTP communication

The Employee Service uses `requests.get()` to look up a department and `requests.post()` to send a notification. The `timeout=5` argument limits how long a call may wait.

### Exception and status handling

FastAPI raises `404` when a department does not exist and `502` when the Department Service cannot be reached or reject the request. Notification failure is represented inside the employee registration response instead of rolling back the employee registration.

### Payroll calculation

The Payroll Service calculates a fixed percentage-based breakdown:

- HRA: 20% of basic salary
- Allowance: 10% of basic salary
- Gross salary: basic salary plus HRA plus allowance
- Tax: 10% of gross salary
- Net salary: gross salary minus tax

### In-memory storage

The Employee Service keeps employees in a Python list and the Department Service keeps departments in a dictionary. Restarting the service clears data not stored in a database or another persistent system.

## Project Structure

```text
SOA_Employee_Management/
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

## Important Files

### `department_service/main.py`

Defines the Department Service and two endpoints:

- `GET /` reports that the service is running.
- `GET /departments/{department_id}` retrieves one department.
- `GET /departments` lists all departments.

The fixed department dictionary contains:

| ID | Department |
|---:|---|
| 101 | IT |
| 102 | HR |
| 103 | Finance |

Unknown IDs return `404` with `Department not found`.

### `employee_service/main.py`

Is the main employee registration service. Its `EmployeeRequest` requires a name, valid email, department ID, and salary.

For `POST /employees`, it performs this workflow:

1. Calls `GET http://127.0.0.1:8002/departments/{department_id}`.
2. If the department call fails, raises `502` with `Department Service unavailable or request failed`.
3. Creates an employee with an ID based on the current list length.
4. Stores the employee in memory.
5. Calls `POST http://127.0.0.1:8004/notifications`.
6. If notification succeeds, adds the notification response to the registration response.
7. If notification fails, keeps the employee and records `status: "FAILED"` instead.

`GET /employees` returns the current in-memory employee list.

### `notification_service/main.py`

Defines a `NotificationRequest` containing employee name, `EmailStr`, and message. `POST /notifications` prints:

- `Sending notification...`
- employee name
- email
- message

It then returns `status: "SUCCESS"` rather than contacting an external email provider. Thus, this is simulated notification behavior.

### `payroll_service/main.py`

Defines `PayrollRequest` with `employee_id` and `basic_salary`. `basic_salary` must be greater than zero because Pydantic uses `Field(gt=0)`.

`POST /payroll/calculate` returns:

- employee ID
- basic salary
- HRA
- allowance
- gross salary
- tax
- net salary

### `requirements.txt`

Lists `fastapi`, `uvicorn`, `requests`, and `email-validator`.

## How the Services Work Together

The services communicate through local HTTP addresses:

```text
Employee Service (:8001)
    ├── GET Department Service (:8002) for department validation
    ├── POST Notification Service (:8004) for registration notification
    └── independent Payroll Service (:8003) for salary calculation
```

An employee registration begins at the Employee Service. The department ID is validated before a new employee is created. The new employee's department name is added to the employee record. A notification is then attempted, but notification failure does not remove the employee.

The Payroll Service is independent of employee registration and is called directly as needed.

## Libraries and Tools

| Library or tool | Used for | Why it is used |
|---|---|---|
| FastAPI | REST framework | Turns the four Python modules into HTTP services |
| Uvicorn | ASGI server | Runs each service on a separate port |
| Pydantic | Request validation | Checks request fields, types, positive values, and email formats |
| `EmailStr` | Email validation | Requires a syntactically valid email address |
| `email-validator` | Email syntax implementation | Supplies Pydantic's `EmailStr` validation |
| `requests` | Cross-service HTTP | Allows the Employee Service to call Department and Notification services |

## Setup

Run the setup commands from the repository root:

```bash
cd SOA_Employee_Management
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
cd SOA_Employee_Management
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Running the Services

Open four terminals, activate the same virtual environment in each terminal, and use these commands.

### Department Service: port 8002

```bash
uvicorn department_service.main:app --port 8002 --reload
```

Swagger: `http://127.0.0.1:8002/docs`

### Employee Service: port 8001

```bash
uvicorn employee_service.main:app --port 8001 --reload
```

Swagger: `http://127.0.0.1:8001/docs`

### Payroll Service: port 8003

```bash
uvicorn payroll_service.main:app --port 8003 --reload
```

Swagger: `http://127.0.0.1:8003/docs`

### Notification Service: port 8004

```bash
uvicorn notification_service.main:app --port 8004 --reload
```

Swagger: `http://127.0.0.1:8004/docs`

Uvicorn should be launched from `SOA_Employee_Management/`, where Python can find the `department_service`, `employee_service`, `notification_service`, and `payroll_service` packages.

## Expected API Behavior

### Department response

`GET /departments/101` returns:

```json
{"id": 101, "name": "IT"}
```

Unknown department IDs return `404`.

### Employee registration

Send `POST http://127.0.0.1:8001/employees`:

```json
{
  "name": "Abhishek",
  "email": "abhishek@example.com",
  "department_id": 101,
  "salary": 50000
}
```

The expected response includes the new employee, department name, success message, and notification status.

`GET /employees` at port `8001` returns the employees currently stored in memory.

If the Department Service is unavailable or rejects the lookup, registration returns `502`.

If the notification call fails, the employee remains registered and the response contains:

```json
{
  "status": "FAILED",
  "message": "Employee registered, but notification failed"
}
```

If notification succeeds, the Notification Service response contains:

```json
{
  "status": "SUCCESS",
  "message": "Notification sent to abhishek@example.com"
}
```

The Notification Service terminal prints the notification details.

### Payroll calculation

Send `POST http://127.0.0.1:8003/payroll/calculate`:

```json
{
  "employee_id": 1,
  "basic_salary": 50000
}
```

The expected calculation is:

| Component | Amount |
|---|---:|
| Basic salary | ₹50,000 |
| HRA | ₹10,000 |
| Allowance | ₹5,000 |
| Gross salary | ₹65,000 |
| Tax | ₹6,500 |
| Net salary | ₹58,500 |

A basic salary of zero or a negative value is rejected because `Field(gt=0)` requires a value greater than zero.

## Errors and Limitations

- Employee and department data is held in memory, not in a database.
- Restarting the Employee Service clears registered employees.
- Restarting the Department Service restores the fixed department dictionary.
- No real email is sent. The Notification Service only prints to the terminal.
- The Employee and Payroll services do not share data or database models.
- Hard-coded local addresses assume that every service runs on `127.0.0.1` and the specified port.
- Department lookup failure returns `502`.
- Notification failure returns a partial-success response and does not remove the registered employee.
- No authentication or authorization protects endpoints.
- There is no service registry or discovery, so changing a port or host requires editing source code.
- There are no retries, circuit breakers, distributed tracing, queues, migrations, or automated tests.
- Employee IDs are based on list length, so ID behavior is only suitable for this in-memory example.

## What to Study Next

Study persistent storage for each service, service discovery or configuration for hosts and ports, authentication, retries and circuit breakers, message queues for notifications, and distributed tracing.

To compare this architecture with a database-backed layered implementation, continue with [employee_app/README.md](../employee_app/README.md).
