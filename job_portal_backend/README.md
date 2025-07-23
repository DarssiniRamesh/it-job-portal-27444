# IT Job Portal Backend

This is the backend API for the IT Job Portal application, built with **FastAPI**. It manages user authentication, job postings, applications, profile management, and dashboard statistics for both job seekers and employers.

## Major Features

- **User registration & authentication** (JWT-based)
- **Job CRUD:** Add, update, search, and delete job postings
- **Applications:** Job seekers apply and track applications, employers manage applications
- **Profile management** for job seekers
- **Role-based access:** Admin, Employer, Job Seeker
- **Dashboard endpoints** for aggregate statistics for both employers and job seekers
- **RESTful API** with documented OpenAPI (Swagger) spec

## Project Structure

- `src/api/`: API entrypoints (endpoints, models, schemas, auth)
- `interfaces/openapi.json`: OpenAPI spec for all endpoints
- `requirements.txt`: Python package dependencies

## Setup Instructions

1. **Clone the repo & enter the backend directory:**
    ```sh
    git clone <repo-url>
    cd it-job-portal-27444/job_portal_backend
    ```

2. **Create & activate a virtual environment:**
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4. **Set required environment variables**  
   (if using a `.env` file, please create it in this directory. Example – add DB connection if used):

    ```env
    DATABASE_URL=sqlite:///./job_portal.db
    SECRET_KEY=your-secret-key
    ```

5. **Run development server:**
    ```sh
    uvicorn src.api.main:app --reload
    ```
   The backend will be available at `http://localhost:8000`

## API Documentation

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **OpenAPI Spec (JSON):** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)
- **Static OpenAPI Spec:** See [`interfaces/openapi.json`](./interfaces/openapi.json)

## API Overview

The backend exposes a comprehensive REST API. Categories include:

- **/auth/**: User Registration & JWT login
- **/users/**: User management (CRUD for admins)
- **/profiles/**: Job seeker profiles
- **/jobs/**: Jobs CRUD & search
- **/applications/**: Application submission & management
- **/dashboard/**: Aggregated statistics

Refer to [OpenAPI spec](./interfaces/openapi.json) for request/response models.

## Deployment & Previews

- For local deployment, see the steps above.
- For Dockerized/cloud deployment, configure environment variables like `DATABASE_URL`, `SECRET_KEY`, etc., as per your host.
- Use tools like Uvicorn’s production settings for serving APIs.

## Special Notes

- Make sure you have a running database if you change `DATABASE_URL`.
- JWT secret must be unique per deployment.
- To preview API or run tests, use FastAPI’s built-in interactive docs or tools like `curl`/Postman.
