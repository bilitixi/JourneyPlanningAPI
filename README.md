# Journey Planning Cloud Application

## Project Overview

Journey Planning Cloud Application is a cloud-based web application that helps users create, manage, and organize travel journeys.

The system provides RESTful API endpoints for:

* Journey management
* Weather forecasting
* AI-generated travel recommendations
* User authentication and authorization
* API usage monitoring

Users must register and authenticate before accessing protected endpoints. The application records API usage logs to support monitoring, auditing, and analytics.

---

# Features

* User Registration and Login
* JWT Authentication and Authorization
* Journey CRUD Operations
* Weather Forecast Integration
* AI Travel Recommendations
* API Usage Logging
* Admin Reporting Endpoints
* MySQL Database Integration
* RESTful API Architecture
* Automated Testing using Pytest

---

# Technology Stack

## Backend

* Python
* Flask
* Flask-JWT-Extended
* SQLAlchemy
* MySQL

## External Services

* OpenWeather API / WeatherAPI
* OpenAI API

## Testing

* Pytest

## DevOps

* GitHub
* GitHub Actions (CI/CD)

---

# MySQL Database Setup

## Prerequisites

- MySQL database running in Docker container
- Python 3.8 or higher
- Docker installed and running

## Setting Up Docker MySQL Container

To set up the MySQL database in a Docker container, run the following command:

```bash
docker run -d --name journey_mysql -e MYSQL_ROOT_PASSWORD=Unitec123 -e MYSQL_DATABASE=journey_planning -e MYSQL_USER=user -e MYSQL_PASSWORD=Unitec123 -p 3306:3306 mysql:latest
```

This command creates a MySQL container with:
- Container name: `journey_mysql`
- Database: `journey_planning`
- User: `user` with password `Unitec123`
- Root password: `Unitec123`
- Port mapping: `3306:3306` (host:container)

To verify the container is running:

```bash
docker ps
```

To view container logs:

```bash
docker logs journey_mysql
```

To stop the container:

```bash
docker stop journey_mysql
```

To start the container:

```bash
docker start journey_mysql
```

## Docker MySQL Container Connection

The application connects to an existing MySQL database running in a Docker container.

### Environment Configuration

Create or update the `.env` file in the project root with your Docker MySQL container details:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=user
MYSQL_PASSWORD=Unitec123
MYSQL_DATABASE=journey_planning
```

### Connection Options

**Option 1: Same Docker Network**
If your application runs in the same Docker network as the MySQL container:
```env
MYSQL_HOST=mysql  # Container name
```

**Option 2: Host to Container**
If your application runs on the host machine:
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306  # Or the mapped port from Docker
```

**Option 3: Docker Compose**
If using Docker Compose, ensure both services are in the same network:
```yaml
services:
  app:
    depends_on:
      - mysql
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: journey_planning
```

## Testing Connection

Test the MySQL connection by running:

```bash
python db.py
```

You should see: `MySQL database connection successful!`

## Initializing Tables

The database tables will be automatically created when you start the application. The `init_db()` function in `db.py` handles table creation based on your SQLAlchemy models.

To manually initialize tables:

```python
from db import init_db
init_db()
```

## Troubleshooting

### Connection Refused

- Ensure the MySQL Docker container is running: `docker ps`
- Check that the host in `.env` matches your Docker setup
- Verify the container is accessible from your application

### Access Denied

- Verify username and password in `.env` match Docker container credentials
- Check MySQL container environment variables

### Database Not Found

- Ensure the database exists in the Docker container
- Check the database name in `.env` matches the container database
- Connect to the container to verify: `docker exec -it <container_name> mysql -u root -p`

---

# Database Design

## Users Table

Stores registered users.

| Column        | Type                    | Description       |
| ------------- | ----------------------- | ----------------- |
| id            | INT, PK, Auto Increment | Unique user ID    |
| first_name    | VARCHAR                 | User first name   |
| last_name     | VARCHAR                 | User last name    |
| email         | VARCHAR                 | User email        |
| password_hash | VARCHAR                 | Hashed password   |
| role          | VARCHAR                 | user/admin        |
| created_at    | TIMESTAMP               | Registration date |

### Rules

* Passwords are hashed using bcrypt.
* Plain text passwords are never stored.
* Email addresses must be unique.

---

## Journeys Table

Stores journey information.

| Column      | Type                    | Description         |
| ----------- | ----------------------- | ------------------- |
| journey_id  | INT, PK, Auto Increment | Journey ID          |
| user_id     | INT, FK                 | Journey owner       |
| destination | VARCHAR                 | Destination         |
| start_date  | DATE                    | Journey start date  |
| end_date    | DATE                    | Journey end date    |
| budget      | DECIMAL                 | Planned budget      |
| people      | INT                     | Number of travelers |
| notes       | TEXT                    | Additional notes    |
| created_at  | TIMESTAMP               | Creation date       |

### Example

| Destination | Start Date | End Date   | Budget | People |
| ----------- | ---------- | ---------- | ------ | ------ |
| Auckland    | 2026-06-01 | 2026-06-05 | 1200   | 2      |
| Queenstown  | 2026-07-10 | 2026-07-15 | 2500   | 3      |

---

## API Usage Logs Table

Tracks API activity.

| Column      | Type      |
| ----------- | --------- |
| id          | INT, PK   |
| user_id     | INT, FK   |
| endpoint    | VARCHAR   |
| method      | VARCHAR   |
| parameters  | TEXT      |
| status_code | INT       |
| created_at  | TIMESTAMP |

Used to track:

* User activity
* Endpoint usage
* Request timestamps
* Success and failure responses

---

# Authentication

The application uses JWT (JSON Web Token) authentication.

## Register

```http
POST /api/auth/register
```

### Request

```json
{
  "first_name": "John",
  "last_name": "Smith",
  "email": "john@example.com",
  "password": "Password123"
}
```

### Response

```json
{
  "message": "User registered successfully"
}
```

---

## Login

```http
POST /api/auth/login
```

### Request

```json
{
  "email": "john@example.com",
  "password": "Password123"
}
```

### Response

```json
{
  "access_token": "jwt_token_here",
  "user": {
    "id": 1,
    "email": "john@example.com"
  }
}
```

---

## Authorization Header

Protected endpoints require:

```http
Authorization: Bearer <jwt_token>
```

---

## Update Account

```http
PUT /api/auth/me
```

Updates the authenticated user's own profile. Requires a valid JWT. All fields are optional; only the fields provided are updated. `current_password` is required only when changing `email` or `password`.

### Request

```json
{
  "first_name": "John",
  "last_name": "Smith",
  "email": "new-email@example.com",
  "password": "NewPassword123",
  "current_password": "OldPassword123"
}
```

### Response

```json
{
  "message": "User updated successfully",
  "user": {
    "id": 1,
    "first_name": "John",
    "last_name": "Smith",
    "email": "new-email@example.com",
    "role": "user",
    "created_at": "2026-07-19T10:30:00"
  }
}
```

---

## Delete Account

```http
DELETE /api/auth/me
```

Deletes the authenticated user's own account and all of their journeys. Requires a valid JWT and password confirmation.

### Request

```json
{
  "current_password": "Password123"
}
```

### Response

```json
{
  "message": "Account deleted successfully"
}
```

---

# API Endpoints

## Journey Endpoints

### Get All Journeys

```http
GET /api/journeys
```

Returns all journeys belonging to the authenticated user.

### Get Journey Details

```http
GET /api/journeys/{id}
```

Returns a specific journey.

### Create Journey

```http
POST /api/journeys
```

#### Request

```json
{
  "destination": "Queenstown",
  "start_date": "2026-07-10",
  "end_date": "2026-07-15",
  "budget": 2500,
  "people": 3,
  "notes": "Winter holiday"
}
```

### Update Journey

```http
PUT /api/journeys/{id}
```

### Delete Journey

```http
DELETE /api/journeys/{id}
```

---

## Weather Endpoint

### Get Weather Forecast

```http
GET /api/weather/{journey_id}
```

Returns weather forecast information for the journey destination.

### Example Response

```json
{
  "destination": "Auckland",
  "forecast": [
    {
      "date": "2026-06-01",
      "temperature": 18,
      "condition": "Cloudy",
      "rain_probability": 20
    }
  ]
}
```

### Weather Providers

* OpenWeather API
* WeatherAPI

---

## AI Recommendation Endpoint

### Generate Recommendations

```http
POST /api/recommendations/{journey_id}
```

Generates travel recommendations based on:

* Destination
* Travel dates
* Budget
* Number of travelers

### Example Response

```json
{
  "destination": "Queenstown",
  "recommendations": [
    "Skyline Gondola",
    "Milford Sound Tour",
    "Lake Wakatipu",
    "Ben Lomond Track"
  ]
}
```

---

## Admin Endpoint

### View API Logs

```http
GET /api/admin/logs
```

Admin users can retrieve API usage logs.

### Example Response

```json
{
  "count": 2,
  "logs": [
    {
      "id": 1,
      "user_id": 1,
      "endpoint": "/api/journeys",
      "method": "GET",
      "status_code": 200,
      "created_at": "2026-06-01 10:30:00"
    }
  ]
}
```

---

# HTTP Status Codes

| Code | Meaning                     |
| ---- | --------------------------- |
| 200  | Successful GET, PUT, DELETE |
| 201  | Successful POST             |
| 400  | Invalid Request             |
| 401  | Unauthorized                |
| 403  | Forbidden                   |
| 404  | Not Found                   |
| 500  | Internal Server Error       |

---

# Project Structure

```text
JourneyPlanningAPI/
│
├── app.py
│
├── routes/
│   ├── auth_routes.py
│   ├── journey_routes.py
│   ├── weather_routes.py
│   ├── recommendation_routes.py
│   └── admin_routes.py
│
├── services/
│   ├── weather_service.py
│   ├── ai_service.py
│   └── auth_service.py
│
├── models/
│   ├── user.py
│   ├── journey.py
│   └── api_usage_log.py
│
├── middleware/
│   ├── jwt_auth.py
│   └── request_logger.py
│
├── tests/
│   ├── test_auth.py
│   ├── test_journeys.py
│   ├── test_weather.py
│   └── test_recommendations.py
│
├── db.py
├── requirements.txt
├── pytest.ini
├── .env
└── README.md
```

---

# Testing

The project uses Pytest for automated testing.

Run tests locally:

```bash
pytest
```

Test modules:

* test_auth.py
* test_journeys.py
* test_weather.py
* test_recommendations.py

---

# Continuous Integration

GitHub Actions automatically runs tests whenever code is pushed or a pull request is created.

Workflow includes:

1. Install dependencies
2. Build application
3. Run pytest
4. Report results

Pull requests should pass all tests before merging into the main branch.

---

# Future Improvements

* Journey Budget Analysis
* Multi-city journeys
* Journey sharing
* Email notifications
* Interactive maps
* Booking integration

---

# Summary

This project demonstrates:

* Cloud-based application architecture
* JWT authentication and authorization
* RESTful API development
* MySQL database integration
* External API integration
* AI-powered recommendations
* API usage monitoring
* Automated testing with Pytest
* Continuous Integration with GitHub Actions

The main goal of this project is to showcase how modern cloud applications integrate authentication, external services, AI capabilities, testing, and deployment into a scalable solution.
