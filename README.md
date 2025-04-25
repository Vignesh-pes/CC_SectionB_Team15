Virtual Labs Microservices - Team 15 & Collaborators
This repository contains microservices developed by Team 15 for a Virtual Labs platform, along with integrations with services developed by Team 9. The platform aims to provide a comprehensive virtual laboratory experience for students.

Project Goal
To develop a robust and scalable backend system for a Virtual Labs platform, enabling secure user management, access control, and essential lab functionalities through a microservice architecture
Microservices Overview
This project follows a microservice architecture. Team 15 was responsible for the following core services:

User Registration: Handles new user sign-up and profile data collection.   
Profile Management: Allows users to view and update their profile details.   
Authentication: Manages user login, session management using JWTs, and inter-service token validation. Integrates with Team 9's MFA service.   
Role-Based Access Control (RBAC): Manages roles, permissions, assignments, and access checks. Integrates with Team 9's Activity Log service.   
Notification: Handles the creation and storage of in-app notifications, intended to be triggered by events.   
Key integrations with Team 9 services:

Multi-Factor Authentication (MFA): (Developed by Vanshika Ashok Jadhav, Team 9) Integrated into the Authentication flow.
Activity Logs: (Developed by Nishitha, Team 9) Used by the RBAC service to log significant events.
Microservice Details

1. User Registration Service
Description: Allows new students to create accounts, providing essential personal, educational, and course enrollment details. Features include data validation and triggering post-registration events.   
Technology Stack:
Frontend: React (Vite), MUI, Axios    
Backend: Node.js, Express.js, Supabase Client (@supabase/supabase-js), CORS, dotenv    
Database: Supabase (Auth for credentials, PostgreSQL for profiles table)    
Eventing: Supabase Database Webhooks, Supabase Edge Functions    
Containerization: Docker, Docker Compose    
API: POST /register (Handles Supabase Auth signup and profile insertion)    
Setup: Refer to the service's specific README for details on environment variables (.env), Supabase setup, and Docker commands.
2. Profile Management Service
Description: Enables users to create, view, and update their profile information, including personal details, educational background, and course enrollment.   
Technology Stack:
Backend: Python, Flask, Flask-WTF, Flask-CORS    
Database: Currently uses an in-memory dictionary for simplicity; intended for use with a persistent database in production.   
Containerization: Docker    
API:
POST /api/profiles: Create profile    
GET /api/profiles/<user_id>: Retrieve profile    
PUT /api/profiles/<user_id>: Update profile    
Setup: Refer to the service's specific README. Includes app.py, index.html, script.js, style.css. Docker build/run commands provided. Integration with other services can be via REST APIs or a message broker.   
3. Authentication Service (Integrated with MFA)
Description: Provides secure user login (email/password), JWT generation/validation, session control, and endpoints for inter-service token/role verification. This service is integrated with an MFA microservice developed by Team 9.   
Developed By: Nagathejas M S (Team 15 - Core Auth), Vanshika Ashok Jadhav (Team 9 - MFA)
Directory: User-Authentication(integrated-with-MFA)/ (Confirm based on initial prompt)
Technology Stack (Core Auth):
Frontend: React (CRA), React Router, Axios, jwt-decode    
Backend: Node.js, Express.js, bcryptjs, jsonwebtoken, Supabase Client (@supabase/supabase-js), CORS, dotenv    
Database: Supabase (PostgreSQL) for users table (email, hashed password, role) with RLS    
Containerization: Docker, Docker Compose    
Technology Stack (MFA - Team 9): Python, Flask, Flask-Mail, Supabase, Flask-CORS, Docker (Based on initial prompt)
API (Core Auth):
POST /api/auth/login    
POST /api/auth/logout    
GET /api/auth/validate    
POST /api/service/validate-token    
POST /api/service/get-user-role    
GET /health    
API (MFA - Team 9): 
POST /generate-otp
POST /verify-otp
4. Role-Based Access Control (RBAC) Service (Integrated with Activity Logs)
Description: Centralized management of roles and permissions, assignment to users, and an access control check endpoint (/check). This service integrates with an Activity Log microservice developed by Team 9.   
Developed By: Sreekar Samrudh (Team 15 - RBAC), Nishitha (Team 9 - Activity Logs)
Directory: rbac_service/ (Confirm based on initial prompt)
Technology Stack (RBAC):
Backend: Python 3.11, FastAPI, Uvicorn, SQLAlchemy 2.x, Alembic, Pydantic 2.x    
Database: PostgreSQL 15, psycopg2-binary    
Containerization: Docker, Docker Compose    
Dependencies: httpx (for calling Activity Logs), python-dotenv, pydantic-settings 
Technology Stack (Activity Logs - Team 9): Node.js/Express.js, MongoDB (Based on initial prompt)
API (RBAC): All under /api/v1/ prefix:
Roles: POST /roles, GET /roles, GET /roles/{role_id}, PUT /roles/{role_id}, DELETE /roles/{role_id}   
Permissions: POST /permissions, GET /permissions, GET /permissions/{permission_id}, PUT /permissions/{permission_id}, DELETE /permissions/{permission_id}   
Assignments: POST /roles/{role_id}/permissions, DELETE /roles/{role_id}/permissions/{permission_id}, POST /users/{user_id}/roles, GET /users/{user_id}/roles, DELETE /users/{user_id}/roles/{role_id}    
Check: POST /check    
Health: GET /    
Data Storage (RBAC): PostgreSQL managed via Docker Compose with a named volume (postgres_data). Schema includes roles, permissions, role_permissions, user_roles tables, managed by Alembic migrations.   
Setup: Refer to the service's specific README (likely in rbac_service/). Requires .env file, correct placement of Team 9's Activity Log service for build context, and running Alembic migrations (docker-compose exec app alembic upgrade head) after container startup. Management endpoints likely require JWT authentication.   
5. Notification Service
Description: Creates and stores in-app notifications for users. Designed to be triggered by events from other microservices (e.g., via a message broker). Currently includes a test endpoint for simulation.   
Technology Stack:
Backend: Python, Flask, pymongo    
Database: MongoDB    
Containerization: Docker    
API:
GET /test-in-app-notification/<user_id>    
Data Storage: MongoDB instance (likely containerized), using notification_db database and in_app_notifications collection. Stores user_id, notification_type, message, created_at, is_read.   
Setup: Refer to the service's specific README. Uses Docker for the service and MongoDB. Requires linking the service container to the MongoDB container. Full integration requires setting up a message broker.   
General Prerequisites
Docker (https://docs.docker.com/get-docker/)
Docker Compose (https://docs.docker.com/compose/install/)
Git (https://git-scm.com/downloads)
Access to Supabase (for Auth, Registration, and potentially MFA services)
Overall Setup & Running
This project consists of multiple independent microservices, each potentially with its own docker-compose.yml file and setup instructions.

General Approach:

Clone the repository:
Bash

git clone https://github.com/Vignesh-pes/CC_SectionB_Team15
cd CC_SectionB_Team15
Navigate into each microservice directory 
Follow the specific README.md file within that directory for detailed setup instructions, including:
Creating and configuring necessary .env files with secrets and URLs (e.g., Supabase keys, database URLs, JWT secrets, Mail credentials). Do not commit .env files to Git.
Setting up required database schemas or tables (e.g., Supabase tables, running Alembic migrations).
Building Docker images (docker-compose build).
Running the services (docker-compose up -d).


Contributors
Team 15:
Vignesh --> PES1UG22AM074(Profile Management , Notification Service) 
Sreekar Samrudh-->PES1UG22AM080 (RBAC)
Nagathejas M S-->PES1UG22AM088 (Authentication)
Bharteesha-->PES1UG22AM098 (Registration)

Team 9 (Collaborators):
Vanshika Ashok Jadhav (MFA Service)
Nishitha (Activity Log Service)
