# Event Reservation API

A RESTful backend API built with Python and FastAPI for managing event ticket reservations, customer accounts, and access-controlled reservation operations.

## Features

- Create event ticket reservations with availability validation.
- Prevent overbooking and restore tickets after cancellation.
- Support guest reservations without requiring an account.
- Register customer accounts with hashed passwords.
- Authenticate users using Bearer Access Tokens.
- Associate reservations with registered customer accounts.
- Link an existing guest reservation during Sign Up using its Reservation ID and Confirmation Code.
- Restrict reservation details and cancellations to authorized customers.
- Retrieve reservation history, including cancelled bookings.
- Search reservations by event with pagination.
- Return structured JSON responses and appropriate HTTP status codes.

## Technologies

- Python
- FastAPI
- Pydantic
- Uvicorn
- pwdlib / Argon2
- HTTP Bearer Authentication

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Start the API server:

```bash
python -m uvicorn main:app
```

Open the interactive API documentation:

`http://127.0.0.1:8000/docs`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/main_page/sign_up` | Register a customer account |
| POST | `/main_page/login` | Authenticate and obtain an Access Token |
| POST | `/reservations/event_name/tickets` | Create a guest or authenticated reservation |
| GET | `/reservations/{event_name}/tickets` | Check available tickets |
| POST | `/cancellations/event_name` | Cancel an authorized reservation |
| GET | `/reservations/details/client/{reservation_id}` | View an owned reservation and its status |
| GET | `/reservations/details/{event_name}` | List the authenticated customer's active reservations for an event |

## Authentication and Authorization

The API uses Bearer Tokens for authenticated operations.

Customers can make reservations without logging in. When an authenticated customer creates a reservation, it is automatically associated with their account.

Protected operations validate the Access Token and verify that the customer has permission to access the requested reservation.

## Data Storage

This project uses in-memory Python data structures instead of a database.

All reservations, accounts, and authentication tokens are reset when the server restarts.

## Project Status

Educational backend development project demonstrating REST API development, request validation, authentication, authorization, and reservation management.

The current implementation is intended for local development and learning, not production deployment.