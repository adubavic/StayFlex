# StayFlex

A modern voucher marketplace for hotel experience packages. Inspired by Dakota Box, StayFlex allows users to purchase curated experience packages that can be redeemed at partner properties.

## Features

- **Experience Packages**: Browse and purchase curated hotel experience packages
- **Gift Vouchers**: Buy vouchers as gifts for loved ones
- **Property Booking**: Redeem vouchers at partner properties
- **User Dashboard**: Manage vouchers and bookings
- **Owner Portal**: Property owners can list their properties and manage bookings
- **Help Center**: Comprehensive FAQ and support resources
- **About & Contact Pages**: Company information and contact forms

## Tech Stack

### Backend
- FastAPI (Python)
- SQLAlchemy 2.0 (Async)
- PostgreSQL
- Redis (Caching)
- JWT Authentication
- Rate Limiting
- Structured Logging

### Frontend
- React 19
- TypeScript
- Tailwind CSS
- shadcn/ui
- React Query
- React Router

## Pages

- **Home** (`/`) - Landing page with featured packages
- **Packages** (`/packages`) - Browse all experience packages
- **Package Detail** (`/packages/:slug`) - Individual package details
- **About** (`/about`) - Company story and values
- **Contact** (`/contact`) - Contact form and support info
- **Help Center** (`/help`) - FAQ and support articles
- **Dashboard** (`/dashboard`) - User dashboard (requires auth)
- **My Vouchers** (`/my-vouchers`) - Manage vouchers (requires auth)
- **Booking** (`/book/:voucherId`) - Book a stay (requires auth)
- **Login** (`/login`) - User authentication
- **Register** (`/register`) - User registration

## Getting Started

### Prerequisites
- Docker
- Docker Compose

### Running with Docker

```bash
# Clone the repository
git clone https://github.com/adubavic/StayFlex.git
cd StayFlex

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Development Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://stayflex:stayflex_dev@localhost:5432/stayflex"
export SECRET_KEY="your-secret-key"

# Run the server
uvicorn server:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## API Documentation

The API documentation is available at `/docs` when running the backend server.

## Environment Variables

### Backend
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT secret key
- `CORS_ORIGINS`: Allowed CORS origins
- `ENVIRONMENT`: development/production
- `LOG_LEVEL`: DEBUG/INFO/WARNING/ERROR
- `PAYSTACK_SECRET_KEY`: Paystack API secret key (for payments)

### Frontend
- `VITE_API_URL`: Backend API URL

## Payment Integration

StayFlex integrates with Paystack for secure payment processing. To enable payments:

1. Sign up for a Paystack account at https://paystack.com
2. Get your test/live API keys from the dashboard
3. Add your secret key to the backend environment variables
4. Configure the frontend with your public key

## License

MIT License
