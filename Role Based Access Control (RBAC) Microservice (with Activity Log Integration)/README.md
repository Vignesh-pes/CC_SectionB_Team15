# Role Based Access Control (RBAC) Microservice (with Activity Log Integration)

## Description
-----------
This project provides a microservice for Role-Based Access Control (RBAC). It allows for the definition and management of roles, permissions, and their assignments to users. It includes functionality to check if a user possesses the required permission for an action.

This service integrates with the **Activity Logs microservice** developed by **Team 9** to record significant events like role creation, permission changes, and assignments.

**Developed By**: Sreekar samrudh (Team 15) 
**Activity Log Service By**: Nishitha (Team 9)


## Project Structure
-----------------
.
├── app/                    # Main application code (FastAPI, SQLAlchemy)
│   ├── api/                # API Router setup
│   │   └── v1/             # Version 1 API
│   │       ├── endpoints/  # Route handler modules
│   │       │   ├── check.py
│   │       │   └── manage.py
│   │       └── api.py      # Main v1 API router
│   ├── core/               # Core logic and configuration
│   │   ├── config.py
│   │   ├── logging_client.py # Client for Activity Log service
│   │   └── security.py     # Authentication/Authorization helpers & dependencies
│   ├── crud/               # Database Create, Read, Update, Delete operations
│   │   └── rbac.py
│   ├── db/                 # Database setup and migrations
│   │   ├── base.py         # SQLAlchemy Base class
│   │   ├── migrations/     # Alembic migration scripts
│   │   │   ├── versions/   # Individual migration files (*.py)
│   │   │   └── env.py      # Alembic environment config
│   │   └── session.py      # Database session management
│   ├── models/             # SQLAlchemy ORM models
│   │   └── rbac.py
│   ├── schemas/            # Pydantic schemas for data validation/serialization
│   │   └── rbac.py
│   └── main.py             # FastAPI application entry point
├── tests/                  # Automated tests (pytest)
│   ├── __init__.py
│   ├── conftest.py         # Pytest fixtures (DB setup, client, overrides)
│   ├── integration/        # Integration tests for API endpoints
│   │   ├── __init__.py
│   │   └── test_manage_api.py
│   └── unit/               # Unit tests for CRUD and core logic
│       ├── __init__.py
│       ├── test_crud.py
│       └── test_security.py
├── .env.example            # Example environment variables
├── .env                    # Actual environment variables (DO NOT COMMIT)
├── .gitignore              # Specifies intentionally untracked files (ensure .env is listed)
├── alembic.ini             # Alembic configuration file
├── docker-compose.yml      # Defines how to build/run RBAC, Postgres, ActivityLogs, MongoDB
├── Dockerfile              # Instructions to build the RBAC service Docker image
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Project metadata and pytest configuration
└── README.md               # This file

## Technologies Used
-----------------
* **RBAC Service (`app`):**
    * Python 3.11+
    * FastAPI
    * SQLAlchemy (ORM)
    * Pydantic (Data validation)
    * Alembic (Database migrations)
    * PostgreSQL (Database via `psycopg2-binary`)
    * python-jose[cryptography] (JWT Handling)
    * httpx (HTTP client for calling Activity Log service)
    * python-dotenv, pydantic-settings (Configuration)
    * Docker
* **Testing:**
    * pytest
    * pytest-asyncio
    * httpx (via `TestClient`)
* **Activity Log Service (Team 9 - Integrated Dependency):**
    * Node.js / Express.js
    * MongoDB
* **Orchestration:**
    * Docker Compose

## Prerequisites
-------------
* Docker (https://docs.docker.com/get-docker/)
* Docker Compose (https://docs.docker.com/compose/install/) (usually included with Docker Desktop)
* Git (https://git-scm.com/downloads)
* Source code for Team 9's Activity Log service placed correctly relative to this project for the `docker-compose.yml` build context.
* Access to an Authentication service capable of issuing JWTs containing a user ID (for using secured endpoints).

## Setup Instructions
------------------
1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Vignesh-pes/CC_SectionB_Team15
    cd rbac_service
    ```

2.  **Configure Environment Variables:**
    * Create a `.env` file in the `rbac_service` root directory by copying `.env.example` (if provided) or creating it manually.
    * Fill in the required values:
        * `DATABASE_URL`: Connection string for the RBAC service's PostgreSQL database (default in `docker-compose.yml` points to the `db` service: `postgresql://user:password@db:5432/rbac_db`).
        * `SECRET_KEY`: A strong, random secret key for JWT validation. Generate one using `python -c "import secrets; print(secrets.token_hex(32))"`. **Keep this secure!**
        * `ALGORITHM`: The JWT algorithm used (e.g., `HS256`). Default is HS256.
        * `ACCESS_TOKEN_EXPIRE_MINUTES`: Default is 30.
        * `ACTIVITY_LOG_SERVICE_URL`: The URL for Team 9's service *within the Docker network*. Default in `logging_client.py` is `http://activity-logs-service:3000/api/activities` - ensure the hostname matches the service name in `docker-compose.yml`.
    * **Important:** The `.env` file contains secrets and should be listed in your `.gitignore` file. Do not commit it.

3.  **Database Setup:**
    * The PostgreSQL and MongoDB databases will be created automatically by Docker Compose.
    * Apply RBAC database migrations using Alembic *after* starting the containers (see Step 5).

4.  **Build Docker Images:**
    * This command builds images for both the RBAC service (`app`) and the Activity Logs service (`activity-logs-service`) based on the merged `docker-compose.yml`.
    ```bash
    docker-compose build
    ```

5.  **Run Containers:**
    * This starts all four services (`db`, `app`, `mongo`, `activity-logs-service`) in detached mode.
    ```bash
    docker-compose up -d
    ```
    * **Apply Migrations:** Once the `db` container is running, apply the Alembic migrations for the RBAC database:
    ```bash
    # Execute alembic upgrade inside the running 'app' container
    docker-compose exec app alembic upgrade head
    ```

## Running the Application
-----------------------
* **Access API Docs (Swagger UI):** `http://localhost:8000/api/v1/docs`
* **Authentication:** Management endpoints (`/roles`, `/permissions`, assignment endpoints) require a valid JWT Bearer token in the `Authorization` header. Use the "Authorize" button in Swagger UI. Tokens should be obtained from your associated Authentication service.
* **Activity Logs:** Actions performed via the management APIs should generate log entries visible via Team 9's Activity Log service API (likely `GET http://localhost:3000/api/activities`).

## API Endpoints (Reference)
-------------------------
Base URL: `/api/v1`

* **Roles**:
    * `POST /roles`: Create a new role (Requires `manage:roles` permission).
    * `GET /roles`: List all roles (paginated).
    * `GET /roles/{role_id}`: Get a specific role by ID.
    * `PUT /roles/{role_id}`: Update a role (Requires `manage:roles` permission).
    * `DELETE /roles/{role_id}`: Delete a role (Requires `manage:roles` permission).
* **Permissions**:
    * `POST /permissions`: Create a new permission (Requires `manage:permissions` permission).
    * `GET /permissions`: List all permissions (paginated).
    * `GET /permissions/{permission_id}`: Get a specific permission by ID.
    * `PUT /permissions/{permission_id}`: Update a permission (Requires `manage:permissions` permission).
    * `DELETE /permissions/{permission_id}`: Delete a permission (Requires `manage:permissions` permission, fails if assigned).
* **Assignments**:
    * `POST /roles/{role_id}/permissions`: Assign a permission to a role (Requires `manage:assignments` permission).
    * `DELETE /roles/{role_id}/permissions/{permission_id}`: Remove a permission from a role (Requires `manage:assignments` permission).
    * `POST /users/{user_id}/roles`: Assign a role to a user (Requires `manage:assignments` permission).
    * `DELETE /users/{user_id}/roles/{role_id}`: Remove a role from a user (Requires `manage:assignments` permission).
    * `GET /users/{user_id}/roles`: List roles assigned to a specific user.
* **Check Permission**:
    * `POST /check`: Check if a user has a specific permission. Requires `{"user_id": "...", "permission": "..."}`. (Typically called by other services).

## Activity Log Integration
-------------------------
This service integrates with Team 9's Activity Log service. Calls are made via background tasks using `httpx` to Team 9's `POST /api/activities` endpoint.

Logged details typically include:
* `userId`: The ID of the user performing the action (or "SYSTEM").
* `action`: A mapped action string (e.g., "permission_change", "other").
* `status`: "success" or "failure".
* `resourceType`: e.g., "Role", "Permission", "UserRoleAssignment".
* `resourceId`: The ID of the affected resource.
* `details`: A JSON object containing specific information like role/permission names or the original RBAC action type.

## Notes
-----
* Management endpoints are protected using JWT Bearer token authentication and specific permission checks (`manage:roles`, `manage:permissions`, `manage:assignments`). Ensure calling clients provide a valid token obtained from an associated Authentication service.
* For the security checks to function correctly, an initial setup is required (typically performed once manually via the API *before* full enforcement or via database seeding):
    1.  Create the permissions: "manage:roles", "manage:permissions", "manage:assignments".
    2.  Create an administrative role (e.g., "Admin").
    3.  Assign these permissions to the "Admin" role.
    4.  Assign the "Admin" role to the user IDs that should have administrative access.