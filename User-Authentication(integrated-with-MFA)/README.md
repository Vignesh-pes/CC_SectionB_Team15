# Virtual Labs - Authentication & MFA Microservices

## Description

This project implements a microservice-based authentication system for a Virtual Labs platform. It includes a core authentication service (backend + frontend) and integrates with a separate Multi-Factor Authentication (MFA) service developed by Vanshika Ashok Jadhav[Team 9]'s team, named [MFA Microservice Name]. The entire system is designed to run using Docker containers managed by Docker Compose.

**Developed By:** Nagathejas M S [Team 15]

**MFA Service By:** Vanshika Ashok Jadhav[Team 9]

## Project Structure

```
.
├── auth-backend/      # Node.js (Express) backend for core authentication (uses Supabase)
│   ├── Dockerfile
│   └── ...
├── auth-frontend/     # React (Vite) frontend for login/MFA UI (served by Nginx)
│   ├── Dockerfile
│   ├── nginx.conf
│   └── ...
├── mfa/               # Flask backend for MFA (OTP generation/verification via Email using Supabase) - [MFA Microservice Name]
│   ├── Dockerfile     # (You might need to add/confirm Dockerfile for this service)
│   ├── requirements.txt
│   ├── init.py
│   └── ...
├── docker-compose.yml # Defines how to build and run all services together
├── .env.example       # Example environment variables for docker-compose
├── .gitignore         # Specifies intentionally untracked files
└── README.md          # This file
```

## Technologies Used

* **Authentication Backend (`auth-backend`):**
    * Node.js
    * Express.js
    * Supabase (for user data via `supabase-js`)
    * Docker
* **Authentication Frontend (`auth-frontend`):**
    * React (Vite)
    * Axios (for API calls)
    * Nginx (for serving static files and API proxying)
    * Docker
* **MFA Service (`mfa` - [MFA Microservice Name]):**
    * Python 3
    * Flask
    * Flask-Mail (with Gmail SMTP)
    * Supabase (for OTP storage via `supabase-py`)
    * Flask-CORS
    * Docker
* **Orchestration:**
    * Docker Compose

## Prerequisites

* [Docker](https://docs.docker.com/get-docker/)
* [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)
* [Git](https://git-scm.com/downloads)

## Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone <your-github-repository-url>
    cd <your-repository-directory>
    ```

2.  **Configure Environment Variables:**
    * **Root Directory:** Create a `.env` file in the project root directory by copying `.env.example`. Fill in the required values:
        * `SUPABASE_URL`: Your Supabase project URL (used by auth-backend).
        * `SUPABASE_ANON_KEY`: Your Supabase project Anon key (used by auth-backend).
    * **MFA Service (`mfa/`)**: Create a `.env` file inside the `mfa/` directory. Fill in the required values based on its `.env.example` (if provided) or `config.py`. This typically includes:
        * `MAIL_USERNAME`: Gmail address used for sending OTPs.
        * `MAIL_PASSWORD`: The 16-digit Google App Password for the `MAIL_USERNAME`.
        * `SUPABASE_URL`: Your Supabase project URL (used by MFA service).
        * `SUPABASE_ANON_KEY`: Your Supabase project Anon key (used by MFA service).
    * **Important:** `.env` files contain secrets and are excluded by `.gitignore`. **Do not commit them to Git.**

3.  **Database Setup:**
    * **Auth Service:** No explicit DB setup needed as it uses Supabase via the API key.
    * **MFA Service:** Ensure the `mfa_otps` table (or similarly named table) is created in your Supabase project as defined in its setup requirements (check previous instructions for the SQL schema).

4.  **Build Docker Images:**
       ```bash
    docker-compose build
    ```

5.  **Run Containers:**
       ```bash
    docker-compose up -d
    ```
6.  Steps 4 and 5 needs to be done 2 times. Once in root folder(parent folder) where you have docker-compose.yml and once in mfa_2 folder where you have docker-compose.yml .
This will start the `auth-backend`, `auth-frontend`, and `mfa` services in detached mode.


## Running the Application

* Access the frontend application in your browser at: `http://localhost:8080` (or the host port you mapped in `docker-compose.yml`).
* Log in using credentials stored in the Supabase custom user table used by the auth-backend.
* If MFA is initiated, check the registered email for the OTP code and verify it via the UI.

## API Endpoints (Reference)

* **Auth Backend:**
    * `POST /api/auth/login`: Verifies user password against Supabase custom user table.
* **MFA Service ([MFA Microservice Name]):**
    * `POST /generate-otp`: Sends an OTP to the provided email. Requires `{"email": "..."}`.
    * `POST /verify-otp`: Verifies the submitted OTP for the given email against Supabase. Requires `{"email": "...", "otp": "..."}`.

## Notes

* The MFA service requires a Gmail account with an **App Password** generated for the email sending to work correctly. Regular passwords will likely fail.
* Ensure the `mfa_otps` table in Supabase is correctly set up before running the MFA flow.
* CORS has been enabled on the MFA service to allow requests from the frontend origin (`http://localhost:8080`).
