# Journey Planning API - Backend Specifications

## Overview
This document provides comprehensive API specifications for the Journey Planning Flask backend, designed for integration with a React frontend application.

**Base URL:** `http://localhost:5000`

**Authentication:** JWT Token-based authentication

---

## Authentication

### JWT Token Structure
Tokens are issued upon successful login and must be included in the `Authorization` header for protected endpoints.

**Header Format:**
```
Authorization: Bearer <access_token>
```

**Token Payload:**
```json
{
  "user_id": 1,
  "email": "user@example.com",
  "role": "user",
  "exp": 1234567890,
  "iat": 1234567890
}
```

**Token Expiration:** 24 hours

**Verification Token Expiration:** 15 minutes

**Reset Token Expiration:** 15 minutes

---

## API Endpoints

### Authentication Endpoints

#### Register User
**POST** `/api/auth/register`

Register a new user account. A verification email will be sent to the provided email address.

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "email": "john@example.com",
  "password": "Password123"
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully. Please check your email to verify your account.",
  "user_id": 1
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Email already registered"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Missing required field: first_name"
}
```

---

#### Login User
**POST** `/api/auth/login`

Authenticate user and receive JWT token. User's email must be verified before logging in.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "Password123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Smith",
    "role": "user"
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "error": "Invalid email or password"
}
```

**Error Response (403 Forbidden):**
```json
{
  "error": "Please verify your email"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "error": "Token is missing"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "error": "Token has expired"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "error": "Invalid token"
}
```

---

#### Verify Email
**POST** `/api/auth/verify-email`

Verify user's email using the verification token sent via email.

**Request Body:**
```json
{
  "token": "verification_token_from_email"
}
```

**Response (200 OK):**
```json
{
  "message": "Email verified successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Invalid verification token"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Verification token has expired"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Missing required field: token"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Token expired"
}
```

---

#### Resend Verification Email
**POST** `/api/auth/resend-verification`

Resend the verification email to a user's email address.

**Request Body:**
```json
{
  "email": "john@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "Verification email sent successfully"
}
```

**Error Response (404 Not Found):**
```json
{
  "error": "User not found"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Already verified"
}
```

**Error Response (429 Too Many Requests):**
```json
{
  "error": "Please wait before requesting another verification email"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Missing required field: email"
}
```

---

#### Forgot Password
**POST** `/api/auth/forgot-password`

Initiate password reset by sending a reset email to the user's email address.

**Request Body:**
```json
{
  "email": "john@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "If email exists, reset sent"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Missing required field: email"
}
```

**Error Response (429 Too Many Requests):**
```json
{
  "error": "Please wait before requesting another password reset email"
}
```

---

#### Reset Password
**POST** `/api/auth/reset-password`

Reset user's password using the reset token sent via email.

**Request Body:**
```json
{
  "token": "reset_token_from_email",
  "new_password": "NewPassword123"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Invalid reset token"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Reset token has expired"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Missing required field: token"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Missing required field: new_password"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Token expired"
}
```

**Error Response (429 Too Many Requests):**
```json
{
  "error": "Please wait before requesting another password reset email"
}
```

---

### Journey Endpoints
*All journey endpoints require JWT authentication*

#### Get All Journeys
**GET** `/api/journeys`

Retrieve all journeys for the authenticated user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "journeys": [
    {
      "journey_id": 1,
      "destination": "Paris",
      "start_date": "2024-06-15",
      "end_date": "2024-06-20",
      "budget": 2500.00,
      "people": 2,
      "notes": "Anniversary trip"
    },
    {
      "journey_id": 2,
      "destination": "Tokyo",
      "start_date": "2024-09-01",
      "end_date": "2024-09-10",
      "budget": 5000.00,
      "people": 1,
      "notes": null
    }
  ]
}
```

---

#### Get Journey by ID
**GET** `/api/journeys/<journey_id>`

Retrieve a specific journey by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**URL Parameters:**
- `journey_id` (integer, required): The ID of the journey

**Response (200 OK):**
```json
{
  "journey_id": 1,
  "destination": "Paris",
  "start_date": "2024-06-15",
  "end_date": "2024-06-20",
  "budget": 2500.00,
  "people": 2,
  "notes": "Anniversary trip"
}
```

**Error Response (404 Not Found):**
```json
{
  "error": "Journey not found"
}
```

---

#### Create Journey
**POST** `/api/journeys`

Create a new journey.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "destination": "Paris",
  "start_date": "2024-06-15",
  "end_date": "2024-06-20",
  "budget": 2500.00,
  "people": 2,
  "notes": "Anniversary trip"
}
```

**Required Fields:**
- `destination` (string): Travel destination
- `start_date` (string): Start date in YYYY-MM-DD format
- `end_date` (string): End date in YYYY-MM-DD format
- `budget` (number): Budget amount
- `people` (integer): Number of travelers

**Optional Fields:**
- `notes` (string): Additional notes

**Response (201 Created):**
```json
{
  "journey_id": 1,
  "destination": "Paris",
  "start_date": "2024-06-15",
  "end_date": "2024-06-20",
  "budget": 2500.00,
  "people": 2,
  "notes": "Anniversary trip"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Missing required field: destination"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Invalid date format"
}
```

---

#### Update Journey
**PUT** `/api/journeys/<journey_id>`

Update an existing journey.

**Headers:**
```
Authorization: Bearer <access_token>
```

**URL Parameters:**
- `journey_id` (integer, required): The ID of the journey

**Request Body (all fields optional except notes cannot be updated):**
```json
{
  "destination": "London",
  "start_date": "2024-07-01",
  "end_date": "2024-07-10",
  "budget": 3000.00,
  "people": 3
}
```

**Note:** The `notes` field cannot be updated via this endpoint.

**Response (200 OK):**
```json
{
  "journey_id": 1,
  "destination": "London",
  "start_date": "2024-07-01",
  "end_date": "2024-07-10",
  "budget": 3000.00,
  "people": 3,
  "notes": "Updated notes"
}
```

**Error Response (404 Not Found):**
```json
{
  "error": "Journey not found"
}
```

---

#### Delete Journey
**DELETE** `/api/journeys/<journey_id>`

Delete a journey.

**Headers:**
```
Authorization: Bearer <access_token>
```

**URL Parameters:**
- `journey_id` (integer, required): The ID of the journey

**Response (200 OK):**
```json
{
  "message": "deleted successfully"
}
```

**Error Response (404 Not Found):**
```json
{
  "error": "Journey not found"
}
```

---

### Weather Endpoints
*Weather endpoints require JWT authentication*

#### Get Weather Forecast
**GET** `/api/weather/<journey_id>`

Get weather forecast for a specific journey.

**Headers:**
```
Authorization: Bearer <access_token>
```

**URL Parameters:**
- `journey_id` (integer, required): The ID of the journey

**Response (200 OK):**
```json
{
  "destination": "Paris",
  "forecast": [
    {
      "date": "2024-06-15",
      "temperature": 22,
      "condition": "Clear sky",
      "rain_probability": 0
    },
    {
      "date": "2024-06-16",
      "temperature": 20,
      "condition": "Light rain",
      "rain_probability": 60
    }
  ]
}
```

**Error Response (404 Not Found):**
```json
{
  "error": "Journey not found or access denied"
}
```

**Error Response (404 Not Found):**
```json
{
  "error": "Location not found"
}
```

**Error Response (404 Not Found):**
```json
{
  "error": "No forecast data available for the selected dates"
}
```

**Error Response (504 Gateway Timeout):**
```json
{
  "error": "Weather service timed out"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "error": "Weather API error: <error details>"
}
```

---

### AI Recommendations Endpoints
*AI recommendation endpoints require JWT authentication*

#### Generate Travel Recommendations
**POST** `/api/recommendations/<journey_id>`

Generate AI-powered travel recommendations for a specific journey using OpenRouter API with NVIDIA Nemotron model.

**Headers:**
```
Authorization: Bearer <access_token>
```

**URL Parameters:**
- `journey_id` (integer, required): The ID of the journey

**Response (200 OK):**
```json
{
  "destination": "Paris",
  "recommendations": [
    "Visit the Eiffel Tower",
    "Explore the Louvre Museum",
    "Walk along the Champs-Élysées",
    "Take a Seine River cruise",
    "Visit Montmartre and Sacré-Cœur"
  ]
}
```

**Note:** If the OpenRouter API fails, the service falls back to predefined recommendations for common New Zealand destinations (Queenstown, Auckland, Wellington, Christchurch) or generic recommendations for other destinations.

**Error Response (404 Not Found):**
```json
{
  "error": "Journey not found"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "error": "Failed to generate recommendations",
  "details": "Error message details"
}
```

---

## Data Models

### User Model
```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Smith",
  "email": "john@example.com",
  "role": "user",
  "is_verified": false,
  "created_at": "2024-01-01T00:00:00"
}
```

**Fields:**
- `id` (integer, auto-generated): Unique user identifier
- `first_name` (string, required): User's first name (max 100 characters)
- `last_name` (string, required): User's last name (max 100 characters)
- `email` (string, required, unique): User's email address (max 255 characters)
- `role` (string, default: "user"): User role ("user" or "admin")
- `is_verified` (boolean, default: false): Email verification status
- `verification_token` (string, nullable): Email verification token
- `verification_expires` (datetime, nullable): Verification token expiration time
- `reset_token` (string, nullable): Password reset token
- `reset_expires` (datetime, nullable): Password reset token expiration time
- `created_at` (datetime, auto-generated): Account creation timestamp

---

### Journey Model
```json
{
  "journey_id": 1,
  "user_id": 1,
  "destination": "Paris",
  "start_date": "2024-06-15",
  "end_date": "2024-06-20",
  "budget": 2500.00,
  "people": 2,
  "notes": "Anniversary trip",
  "created_at": "2024-01-01T00:00:00"
}
```

**Fields:**
- `journey_id` (integer, auto-generated): Unique journey identifier
- `user_id` (integer, required): Foreign key to users table
- `destination` (string, required): Travel destination (max 255 characters)
- `start_date` (date, required): Journey start date (YYYY-MM-DD format)
- `end_date` (date, required): Journey end date (YYYY-MM-DD format)
- `budget` (numeric, required): Budget amount (decimal, max 10 digits, 2 decimal places)
- `people` (integer, required): Number of travelers
- `notes` (text, optional): Additional notes
- `created_at` (datetime, auto-generated): Journey creation timestamp

---

## Error Handling

### Standard Error Response Format
```json
{
  "error": "Error message description"
}
```

### Common HTTP Status Codes
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data or missing required fields
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: Insufficient permissions (admin access required)
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Environment Variables

The backend requires the following environment variables:

**Required:**
- `JWT_SECRET_KEY`: Secret key for JWT token signing (default: "test-secret-key")
- `OPENWEATHER_API_KEY`: API key for OpenWeatherMap service
- `OPENROUTER_API_KEY`: API key for OpenRouter AI service (for recommendations)

**Email Configuration (for email verification and password reset):**
- The backend sends email via SMTP (using Python's `smtplib`)
- Email service configuration is handled in `services/email_service.py`
- Required/optional SMTP environment variables:
  - `MAIL_SERVER`: SMTP server address (default: "smtp.gmail.com")
  - `MAIL_PORT`: SMTP server port (default: 587)
  - `MAIL_USERNAME`: Email username for SMTP authentication
  - `MAIL_PASSWORD`: Email password or app-specific password for SMTP authentication
  - `MAIL_USE_TLS`: Whether to use STARTTLS (default: "true")
  - `MAIL_DEFAULT_SENDER`: From address used for outgoing emails (default: `MAIL_USERNAME`)
- `FRONTEND_URL`: Frontend URL for email verification and reset links (default: "http://localhost:3000")

**Database:**
- `DATABASE_URL`: Full PostgreSQL connection string from cloud provider
- Database configuration is handled in `db.py` (PostgreSQL with SQLAlchemy)
- Note: MySQL configuration is commented out in db.py but available for local development

---

## Authentication Flow

1. **Register:** User creates account via `/api/auth/register`
2. **Verify Email:** User receives verification email and verifies email via `/api/auth/verify-email` (or `/api/auth/resend-verification` to resend)
3. **Login:** User authenticates via `/api/auth/login` to receive JWT token (email must be verified first)
4. **Store Token:** Frontend stores the access_token (localStorage, sessionStorage, or cookie)
5. **Include Token:** Frontend includes token in Authorization header for all protected requests
6. **Token Refresh:** Tokens expire after 24 hours; user must re-login
7. **Password Reset:** If user forgets password, they can request reset via `/api/auth/forgot-password` and complete via `/api/auth/reset-password`

---

## Rate Limiting & Usage

- Rate limiting is implemented for email-related endpoints:
  - Verification email resend: 15-minute cooldown between requests
  - Password reset email: 15-minute cooldown between requests
- API usage is logged in the `api_usage_logs` table for admin monitoring
- Admin users can access usage logs via `/api/admin/logs` (endpoint exists in codebase but not currently registered in main app)

---

## CORS Configuration

The backend has Flask-CORS configured with the following settings:
- **Allowed Origin:** `https://journeyplanninguidraft.vercel.app`
- **CORS Scope:** All `/api/*` endpoints

For local development with a different frontend URL, you may need to:
1. Update the CORS origins in `app.py`, or
2. Configure a proxy in your React development server

---

## Example Integration Code

### React Example - Login
```javascript
const login = async (email, password) => {
  const response = await fetch('http://localhost:5000/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });
  
  const data = await response.json();
  
  if (response.ok) {
    localStorage.setItem('token', data.access_token);
    return data.user;
  } else {
    throw new Error(data.error);
  }
};
```

### React Example - Get Journeys
```javascript
const getJourneys = async () => {
  const token = localStorage.getItem('token');
  
  const response = await fetch('http://localhost:5000/api/journeys', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  
  const data = await response.json();
  
  if (response.ok) {
    return data.journeys;
  } else {
    throw new Error(data.error);
  }
};
```

### React Example - Create Journey
```javascript
const createJourney = async (journeyData) => {
  const token = localStorage.getItem('token');
  
  const response = await fetch('http://localhost:5000/api/journeys', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(journeyData),
  });
  
  const data = await response.json();
  
  if (response.ok) {
    return data;
  } else {
    throw new Error(data.error);
  }
};
```

---

## Notes for Frontend Developers

1. **Date Format:** All dates must be in `YYYY-MM-DD` format
2. **Budget Format:** Budget should be sent as a number (e.g., `2500.00`)
3. **Token Storage:** Store JWT tokens securely; consider using httpOnly cookies for production
4. **Token Expiry:** Handle 401 errors by redirecting to login page; access tokens expire after 24 hours
5. **Error Handling:** Always check response.ok and handle error messages appropriately
6. **User Isolation:** Users can only access their own journeys; the backend enforces this via user_id in JWT payload
7. **Weather Data:** Weather endpoint requires a valid journey_id belonging to the authenticated user
8. **AI Recommendations:** Recommendations endpoint uses OpenRouter API with NVIDIA Nemotron model to generate travel suggestions. Falls back to predefined recommendations for New Zealand cities if API fails.
9. **Database:** Backend uses PostgreSQL database with SQLAlchemy ORM (MySQL configuration available but commented out)
10. **Admin Routes:** Admin routes exist in the codebase (`routes/admin_routes.py`) but are not currently registered in the main app. To enable, register `admin_bp` in `app.py` with appropriate URL prefix.
11. **Token Expiration:** Verification and reset tokens expire after 15 minutes to enhance security.
12. **Rate Limiting:** Rate limiting is implemented for email resend and password reset requests (15-minute cooldown period). Handle 429 errors appropriately.

---

## Testing

The backend includes pytest tests in the `/tests` directory:
- `tests_auth.py`: JWT authentication functionality
- `test_journeys.py`: Journey model and routes
- `test_recommendations.py`: AI recommendation service
- `test_weather.py`: Weather service integration

Run tests with:
```bash
pytest
```

Run specific test file:
```bash
pytest tests/test_weather.py -v
```
