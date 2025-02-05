Milestone 2: Database Modeling and Data Seeding in Django

# Milestone 3: Creating Views and API Endpoints
API Development for Listings and Bookings in Django
Build API views to manage listings and bookings, and ensure the endpoints are documented with Swagger.

## API Endpoints

### Listings

- `GET /api/listings/` – Retrieve a list of all listings
- `POST /api/listings/` – Create a new listing
- `GET /api/listings/{id}/` – Retrieve a specific listing
- `PUT /api/listings/{id}/` – Update a listing
- `DELETE /api/listings/{id}/` – Delete a listing

### Bookings

- `GET /api/bookings/` – Retrieve a list of all bookings
- `POST /api/bookings/` – Create a new booking
- `GET /api/bookings/{id}/` – Retrieve a specific booking
- `PUT /api/bookings/{id}/` – Update a booking
- `DELETE /api/bookings/{id}/` – Delete a booking

# Milestone 4: Payment Integration with Chapa API
## Payment Integration (Chapa API)

This project integrates the Chapa API for payment processing.

### Payment Endpoints:
- `POST /api/payments/initiate/` - Initiates a payment.
- `GET /api/payments/verify/` - Verifies a payment.

### Setup:
1. Add `CHAPA_SECRET_KEY` to `.env`.
2. Run `python manage.py migrate` to apply payment model.
3. Start Celery: `celery -A alx_travel_app worker --loglevel=info`.

### Testing:
Use Chapa sandbox mode for testing payments.