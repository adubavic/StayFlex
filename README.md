# StayFlex Django Backend

A voucher marketplace for hotel experience packages.

## Quick Start

### Using Docker (Recommended)

```bash
# Build and run
docker-compose up --build

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Seed demo data
docker-compose exec backend python manage.py shell < scripts/seed_demo.py
```

### API Documentation

Once running, access the interactive API docs at:
- **Swagger UI**: http://localhost:8000/docs/
- **ReDoc**: http://localhost:8000/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### Local Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e "."

# Copy environment file
cp .env.example .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Seed demo data
python manage.py shell < scripts/seed_demo.py

# Run server
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login/` - JWT login
- `POST /api/v1/auth/refresh/` - Refresh JWT token

### Customer
- `GET /api/v1/voucher-products/` - List voucher products
- `POST /api/v1/vouchers/purchase/` - Purchase voucher
- `GET /api/v1/vouchers/` - List my vouchers
- `POST /api/v1/vouchers/{voucher_id}/eligibility/` - Find eligible offers
- `POST /api/v1/bookings/` - Create booking
- `POST /api/v1/bookings/{booking_id}/otp/request/` - Request OTP

### Owner
- `GET /api/v1/owners/bookings/` - List bookings for my properties
- `POST /api/v1/owners/bookings/{booking_id}/confirm/` - Confirm booking
- `POST /api/v1/owners/bookings/{booking_id}/decline/` - Decline booking
- `POST /api/v1/owners/bookings/{booking_id}/redeem-otp/` - Redeem OTP

### Payments
- `GET /api/v1/paystack/config/` - Get Paystack public key
- `GET /api/v1/payments/verify/` - Verify payment
- `POST /api/v1/payments/webhook/` - Paystack webhook

### Admin
- `GET /api/v1/admin/coverage/` - Coverage metrics
- `POST /api/v1/admin/payouts/{payout_id}/approve/` - Approve payout
- `POST /api/v1/admin/payouts/{payout_id}/mark-paid/` - Mark payout paid

## Architecture

### Models
- **UserProfile** - Extended user profile with role
- **Property** - Accommodation assets with quality scoring
- **OwnerOffer** - Atomic supply units with date ranges
- **OfferInventoryDay** - Per-date capacity tracking
- **VoucherProduct** - Customer-facing SKUs
- **Voucher** - Purchased voucher instances
- **Payment** - Payment transactions
- **Booking** - Reservations
- **Payout** - Owner settlements

### Services
- **EligibilityService** - Match vouchers to eligible offers
- **InventoryService** - Manage offer capacity and reservations
- **PaystackService** - Payment processing
- **OTPService** - OTP generation and verification
- **NotificationService** - WhatsApp and SMS notifications

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=core --cov-report=html
```

## Demo Users (after seeding)
- Admin: `admin` / `admin`
- Owner: `owner` / `owner`
- Customer: `customer` / `customer`
