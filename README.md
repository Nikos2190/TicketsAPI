TicketsAPI
A REST API for managing event ticket reservations, user accounts, and guest bookings. Built with Python and FastAPI as a backend development portfolio project.
Features
- View remaining tickets for supported events.
- Create reservations as a guest or an authenticated user.
- Register an account and log in using token-based authentication.
- Store password hashes rather than plaintext passwords.
- Link an existing guest reservation to an account using its reservation ID and confirmation code, either during sign-up or after login.
- Restrict reservation details and cancellations to the reservation owner.
- Cancel reservations and restore the corresponding ticket inventory.
- List an authenticated user's active reservations for an event, with limit/`offset` pagination.
Tech Stack
- Python 3.10+
- FastAPI and Pydantic
- Uvicorn (ASGI server)
- pwdlib with Argon2 password hashing
- HTTP Bearer authentication
Run Locally
From the project directory containing main.py, install the dependencies:
python -m pip install fastapi uvicorn "pwdlib[argon2]"
Start the server:
python -m uvicorn main:app --reload
Open the interactive API documentation at http://127.0.0.1:8000/docs.
API Endpoints
Method	Endpoint	Description	Authentication
GET	/reservations/{event_name}/tickets	Check remaining tickets	Public
POST	/reservations/event_name/tickets	Create a ticket reservation	Optional
POST	/main_page/sign_up	Create an account; optionally claim a guest reservation	Public
POST	/main_page/login	Log in and receive an access token	Public
POST	/main_page/client	Link a guest reservation to the logged-in account	Required
GET	/reservations/details/client/{reservation_id}	View an owned active or cancelled reservation	Required
GET	/reservations/details/{event_name}	List owned active reservations for an event	Required
POST	/cancellations/event_name	Cancel an owned reservation	Required


Request formats: Sign-up, login, and guest-reservation linking accept JSON request bodies. Ticket creation and cancellation use query parameters. Routes marked Required expect an HTTP Bearer token; enter the token returned by /main_page/login through Swagger UI's Authorize control.
Guest Reservation Workflow
1. Create a reservation through POST /reservations/event_name/tickets without authenticating. Save the returned reservation ID and confirmation code.
2. Create an account through POST /main_page/sign_up and optionally provide these two values in its JSON body. Alternatively, sign up without reservation details, log in, and submit the pair to POST /main_page/client.
3. Once linked, the authenticated account can access the reservation details and cancel the reservation. A reservation cannot be linked to multiple accounts.
The two guest-reservation fields are optional during sign-up but required when linking a reservation through /main_page/client.
Demo Data and Validation
The API starts with three in-memory events:
Event	Initial tickets
AI Conference	100
Music Festival	250
Python Workshop	30


Event names are matched case-insensitively, ignoring spaces. Ticket quantities must be positive and cannot exceed available inventory. Usernames must contain at least three characters; passwords must contain at least eight characters. The API uses HTTP error responses for invalid input, failed authentication, denied access, missing records, and conflicts.
Scope and Limitations
This project is a local, single-process portfolio demonstration, not a production reservation platform.
- In-memory storage: Accounts, reservations, inventory changes, and login tokens are lost when the server restarts.
- Token lifecycle: Login tokens do not expire or support explicit revocation.
- Concurrency: Reservation and inventory updates are not protected against simultaneous requests; multi-worker deployment is not supported by the current storage design.
- No database or deployment infrastructure: Persistence, distributed coordination, and production hardening are intentionally outside the project scope.
These limitations are documented rather than hidden; the focus is on REST API design, validation, password hashing, authentication, authorization, and reservation workflows.