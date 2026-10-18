# TaskFlow — Task Management REST API

TaskFlow is a Python backend project for managing tasks through a REST API. It is built with **FastAPI**, **MySQL**, and **SQLAlchemy**. The application supports user registration and login, JWT-based authentication, user-specific task ownership, task CRUD operations, status filtering, sorting, pagination, and automated tests.

> **Project status:** Developed and tested locally. Deployment to a production hosting platform is not included yet.

## 🚀 Live Demo

- **Live API:** https://taskflow-production-75ba.up.railway.app/
- **Interactive API Documentation (Swagger UI):** https://taskflow-production-75ba.up.railway.app/docs

Explore the API endpoints through Swagger UI to test task management and authentication features.
## Features

- **User registration and login** with password hashing.
- **JWT access tokens** for protected API requests.
- **User-specific task ownership:** users can access and manage only their own tasks.
- **Task CRUD operations:** create, retrieve, update, and delete tasks.
- **MySQL persistence** using SQLAlchemy ORM.
- **Status filtering:** retrieve pending or completed tasks.
- **Sorting:** sort tasks by ID in ascending or descending order.
- **Pagination:** request a limited number of tasks with `limit` and `offset`.
- **Input validation** for task titles, status values, and pagination parameters.
- **Interactive API documentation** through Swagger UI and ReDoc.
- **Automated tests** using pytest, FastAPI TestClient, and an isolated in-memory SQLite test database.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.11 | Application language |
| FastAPI | REST API framework |
| Pydantic | Request validation and response schemas |
| MySQL | Persistent relational database |
| SQLAlchemy | ORM and database access |
| PyMySQL | Python-to-MySQL driver |
| python-dotenv | Load local configuration from `.env` |
| pwdlib with Argon2 support | Password hashing |
| PyJWT | Create and verify JWT access tokens |
| pytest | Automated testing |
| HTTPX / FastAPI TestClient | API testing utilities |
| Git | Version control |

## Project Structure

```text
TaskFlow/
├── api.py             # FastAPI app and task endpoints
├── auth.py            # Registration, login, JWT token utilities
├── database.py        # SQLAlchemy engine, sessions, DB dependency
├── models.py          # SQLAlchemy UserModel and TaskModel
├── create_tables.py   # Create missing database tables
├── check_db.py        # Check the MySQL connection
├── test_api.py        # Automated API tests
├── taskflow_cli.py    # Earlier command-line task manager
├── day3_oop.py        # OOP practice file
├── main.py            # Earlier API practice file, if retained
├── requirements.txt   # Python dependencies
├── .env               # Local secrets/configuration; never commit
├── .gitignore         # Files excluded from Git
└── README.md          # Project documentation
```

Some practice files may vary depending on your current local project. The main API entry point is `api.py`.

## Prerequisites

- Python 3.11 or a compatible Python version
- MySQL Server
- Git
- PowerShell on Windows, or a compatible terminal

## Installation and Setup

### 1. Get the source code

If you have already created a GitHub repository, clone it using the repository URL shown on that repository's GitHub page:

```powershell
git clone https://github.com/MADURAAGANESH-N/TaskFlow.git
cd TaskFlow
```

If the project is already on your computer, open the existing `TaskFlow` folder instead.

### 2. Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script, you can use a process-scoped execution policy for that terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

If you are setting up the project before `requirements.txt` is complete, the dependencies used by the application include:

```powershell
python -m pip install fastapi uvicorn sqlalchemy pymysql python-dotenv "pwdlib[argon2]" PyJWT python-multipart pytest httpx
```

### 4. Create the MySQL database

Open MySQL Workbench or another MySQL client and run:

```sql
CREATE DATABASE IF NOT EXISTS taskflow_db;
```

The database account configured below must have permission to create and modify tables in `taskflow_db`.

### 5. Configure environment variables

Create a file named `.env` in the project root:

```dotenv
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=taskflow_db
SECRET_KEY=YOUR_GENERATED_SECRET_KEY
```

Replace the example values with your own local configuration. Generate a strong, unique secret key on your own computer. For example:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the generated value into `SECRET_KEY` in `.env`.

**Security:** Never commit `.env` to GitHub. Do not publish your MySQL password, JWT secret, access tokens, or other credentials. Ensure `.gitignore` includes at least:

```gitignore
.env
.env.*
venv/
.venv/
__pycache__/
.pytest_cache/
```

### 6. Create database tables

```powershell
python create_tables.py
```

The script uses SQLAlchemy metadata to create tables that do not yet exist.

**Existing database note:** `create_all()` does not alter an existing table to add new columns. If you are upgrading a database created before user ownership was added, check the schema first:

```sql
USE taskflow_db;
DESCRIBE users;
DESCRIBE tasks;
```

If the `tasks.user_id` column is missing, and the `users` table already exists, apply the migration below once. Do not run it if the column or constraint already exists:

```sql
ALTER TABLE tasks
    ADD COLUMN user_id INT NULL,
    ADD INDEX ix_tasks_user_id (user_id),
    ADD CONSTRAINT fk_tasks_user_id
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE;
```

Tasks created before authentication may have `user_id = NULL`. Assign them to a user only if you intentionally want to retain and expose those records to that user.

### 7. Verify the database connection

```powershell
python check_db.py
```

A successful connection prints the selected database and MySQL server version.

### 8. Start the API

```powershell
python -m uvicorn api:app --reload
```

Uvicorn should report that the application is running at `http://127.0.0.1:8000`.

## API Documentation

With the server running, open:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc
- **Home endpoint:** http://127.0.0.1:8000/
- **Health endpoint:** http://127.0.0.1:8000/health

Register an account and log in before calling protected task endpoints. Swagger UI can be used to try the endpoints interactively.

## API Endpoints

### Authentication

| Method | Endpoint | Description | Typical success response |
|---|---|---|---|
| `POST` | `/auth/register` | Create a user account | `201 Created` |
| `POST` | `/auth/login` | Verify credentials and return a JWT access token | `200 OK` |

Login uses form data as required by FastAPI's OAuth2 password flow. Registration uses a JSON request body.

### Tasks

All task endpoints require a valid bearer access token.

| Method | Endpoint | Description | Typical success response |
|---|---|---|---|
| `GET` | `/tasks` | List the current user's tasks | `200 OK` |
| `GET` | `/tasks/{task_id}` | Retrieve one of the current user's tasks | `200 OK` |
| `POST` | `/tasks` | Create a task for the current user | `201 Created` |
| `PATCH` | `/tasks/{task_id}` | Update an owned task's title and/or status | `200 OK` |
| `DELETE` | `/tasks/{task_id}` | Delete an owned task | `204 No Content` |

### List query parameters

`GET /tasks` supports the following parameters:

| Parameter | Allowed values | Default | Description |
|---|---|---|---|
| `status` | `pending`, `completed` | No filter | Return tasks with the selected status |
| `sort` | `asc`, `desc` | `asc` | Sort by task ID |
| `limit` | `1`–`100` | `10` | Maximum tasks to return |
| `offset` | `0` or greater | `0` | Number of matching tasks to skip |

Examples:

```text
GET /tasks
GET /tasks?status=pending
GET /tasks?status=completed&sort=desc
GET /tasks?limit=10&offset=0
GET /tasks?status=pending&sort=asc&limit=5&offset=0
```

### Example request bodies

**Register a user** — `POST /auth/register`:

```json
{
  "username": "example_user",
  "password": "UseYourOwnStrongPassword123!"
}
```

**Create a task** — `POST /tasks`:

```json
{
  "title": "Learn FastAPI"
}
```

**Mark a task as completed** — `PATCH /tasks/{task_id}`:

```json
{
  "status": "completed"
}
```

Use your own credentials for testing; do not use example passwords for real accounts.

## Authentication and Authorization

- Registration stores a password hash rather than the original password.
- Login returns a signed JWT access token.
- Protected endpoints require the token in the `Authorization: Bearer <token>` header.
- Task queries are scoped to the authenticated user's ID.
- A user attempting to retrieve, update, or delete another user's task should receive `404 Not Found`.
- Requests without a valid token should receive `401 Unauthorized`.

The access token lifetime is configured in `auth.py`. Keep the JWT signing secret private and use HTTPS and appropriate production configuration before deploying the API publicly.

## Database Design

### `users`

- `id`: primary key
- `username`: unique username
- `password_hash`: hashed password
- `created_at`: account creation timestamp

### `tasks`

- `id`: primary key with auto-increment
- `user_id`: owner reference to `users.id`
- `title`: task title, up to 120 characters
- `status`: `pending` or `completed`, defaulting to `pending`
- `created_at`: task creation timestamp

MySQL stores the application data persistently. The automated tests use a separate in-memory SQLite database and override the normal database dependency so tests do not alter the development MySQL records.

## Running Automated Tests

Run the test suite from the project root with the virtual environment activated:

```powershell
python -m pytest -v
```

The current test suite was run successfully with **16 tests passing**. Tests cover registration, invalid login credentials, authentication requirements, task CRUD operations, filtering, sorting, pagination, invalid input, and user ownership. Test results can change as code is updated; rerun the suite to confirm the current result.

## Git Workflow

Check working changes:

```powershell
git status
```

Stage specific changes and create a commit:

```powershell
git add README.md
git commit -m "Add TaskFlow project documentation"
git log -1 --oneline
```

Before pushing to GitHub, check that `.env` and other secrets are not tracked:

```powershell
git status
git check-ignore .env
```

## Current Limitations

- The project has been developed and tested locally; production deployment is not included yet.
- Database schema changes to existing tables require an explicit migration; `create_all()` alone does not migrate existing columns.
- Tasks created before user ownership was introduced may have no owner until deliberately migrated or assigned.
- HTTPS setup, production secret management, database backups, rate limiting, and production monitoring need additional configuration before public deployment.

## Future Improvements

- Add database migrations with Alembic.
- Build a frontend for task management.
- Add continuous integration to run tests automatically.
- Add deployment automation and production monitoring.
- Add richer task capabilities, such as due dates, priorities, and search.

## Author

**Maduraaganesh N.**

- GitHub: [MADURAAGANESH-N](https://github.com/MADURAAGANESH-N)

> **Repository URL:** Add your TaskFlow repository link here once the repository has been created or published.
