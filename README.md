# Inventory Management System — Backend API
 
A RESTful API built with Django and Django REST Framework for managing inventory items. Supports JWT authentication, full CRUD operations, stock level monitoring with low-stock alerts, a stock adjustment audit log, email-based password reset via SendGrid, and user profile management with Cloudinary image uploads.
 
This is the backend (middleware + database layer) for the Inventory Management System, built as part of the Enterprise Software Engineering module.
 
## Live Demo
 
- **API Base:** https://inventory-backend-2775.onrender.com/api
- **Swagger Docs:** https://inventory-backend-2775.onrender.com/api/docs/
- **Frontend:** https://inventory-frontend-i2y1.onrender.com
 
> **Note:** The backend runs on Render's free tier, so the first request after inactivity may take up to 60 seconds while the server wakes up.
 
## Features
 
### Authentication
- User registration with email validation
- JWT-based login (access + refresh tokens)
- Password reset via SendGrid email
- User profile management (email, profile image via Cloudinary)
 
### Inventory Management (CRUD)
- Create, read, update, and delete inventory items
- Items are scoped to the authenticated user (user isolation)
- Category system (Electronics, Clothing, Food, Office, Other)
- Low stock threshold per item with computed `is_low_stock` field
- Server-side validation (no negative quantities or thresholds)
 
### Stock Adjustment Audit Log
- Every quantity change is automatically recorded
- Tracks old quantity, new quantity, reason, timestamp, and user
- Accessible via `/api/items/{id}/history/` endpoint
- Reasons are categorised: created, increase, decrease, edit
- Visible in Django admin for oversight
 
### API Documentation
- Swagger UI at `/api/docs/`
- OpenAPI schema at `/api/schema/`
 
## Tech Stack
 
- **Python 3.12**
- **Django 6.0.2**
- **Django REST Framework 3.16.1**
- **Simple JWT** — token-based authentication
- **PostgreSQL** — production database (via Render)
- **SQLite** — local development database
- **SendGrid** — email delivery for password resets
- **Cloudinary** — profile image hosting
- **drf-spectacular** — OpenAPI/Swagger documentation
- **WhiteNoise** — static file serving
- **Gunicorn** — production WSGI server
 
## Project Structure
 
```
django-backend/
├── authentication/          # User auth app
│   ├── models.py           # PasswordResetToken, Profile models
│   ├── serializers.py      # Register, Login, Profile, PasswordReset serializers
│   ├── views.py            # Auth endpoints (register, login, reset, profile)
│   ├── urls.py             # Auth URL routing
│   └── tests.py            # Auth test suite
├── backend/                 # Project settings
│   ├── settings.py         # Django configuration
│   ├── urls.py             # Root URL routing with DRF router
│   └── wsgi.py             # WSGI entry point
├── todo/                    # Inventory app (kept as 'todo' from initial scaffold)
│   ├── models.py           # InventoryItem, StockAdjustment models
│   ├── serializers.py      # Item and StockAdjustment serializers
│   ├── views.py            # ModelViewSet with audit logging
│   ├── admin.py            # Django admin registration
│   └── tests.py            # Inventory + audit log test suite
├── manage.py
└── requirements.txt
```
 
## API Endpoints
 
### Authentication
 
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/register/` | Register new user | No |
| POST | `/api/auth/token/` | Login (get JWT tokens) | No |
| POST | `/api/auth/token/refresh/` | Refresh access token | No |
| POST | `/api/auth/password-reset/` | Request password reset email | No |
| POST | `/api/auth/password-reset-confirm/` | Confirm reset with token | No |
| GET | `/api/auth/profile/` | Get user profile | Yes |
| PATCH | `/api/auth/profile/` | Update user profile | Yes |
 
### Inventory Items
 
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/items/` | List all user's items | Yes |
| POST | `/api/items/` | Create new item | Yes |
| GET | `/api/items/{id}/` | Get specific item | Yes |
| PUT | `/api/items/{id}/` | Full update item | Yes |
| PATCH | `/api/items/{id}/` | Partial update item | Yes |
| DELETE | `/api/items/{id}/` | Delete item | Yes |
| GET | `/api/items/{id}/history/` | Get stock adjustment history | Yes |
 
## Local Setup
 
### Prerequisites
- Python 3.8 or higher
- pip
- Git
 
### Steps
 
```bash
# 1. Clone the repository
git clone <your-repo-url>
cd django-backend
 
# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
 
# 3. Install dependencies
pip install -r requirements.txt
 
# 4. Set up environment variables
# Create a .env file in the project root:
```
 
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
FRONTEND_URL=http://localhost:3000
DEFAULT_PROFILE_IMAGE_URL=https://via.placeholder.com/150
SENDGRID_API_KEY=your-sendgrid-key          # Optional for local dev
DEFAULT_FROM_EMAIL=your-verified@email.com   # Optional for local dev
```
 
```bash
# 5. Run migrations
python manage.py migrate
 
# 6. Create a superuser (optional, for admin access)
python manage.py createsuperuser
 
# 7. Start the development server
python manage.py runserver
```
 
The API will be available at:
- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/
- Swagger: http://localhost:8000/api/docs/
 
## Testing
 
The project includes test suites for both the inventory and authentication apps.
 
```bash
# Run all tests
python manage.py test
 
# Run only inventory tests
python manage.py test todo
 
# Run only authentication tests
python manage.py test authentication
 
# Run with verbosity
python manage.py test -v 2
```
 
### Test Coverage
 
**Inventory tests** cover:
- Model behaviour (low stock calculation, defaults, timestamps)
- Full CRUD via API
- Server-side validation (negative values rejected)
- User data isolation (users only see their own items)
- Authentication enforcement
- Stock adjustment audit log creation
- Audit log reason categorisation (increase/decrease/edit/created)
- History endpoint access control
 
**Authentication tests** cover:
- Registration (success, duplicates, weak passwords, missing fields)
- Login and token refresh
- Profile retrieval and updates
- Password reset token lifecycle
- Security measures (non-existent email returns 200)
 
## Deployment (Render)
 
The backend is deployed as a Web Service on Render.
 
### Environment Variables on Render
 
```
DEBUG=False
SECRET_KEY=<production-secret-key>
DATABASE_URL=<internal-postgres-url>
FRONTEND_URL=https://inventory-frontend-i2y1.onrender.com
SENDGRID_API_KEY=<your-sendgrid-key>
DEFAULT_FROM_EMAIL=<your-verified-email>
DEFAULT_PROFILE_IMAGE_URL=https://via.placeholder.com/150
```
 
### Build & Start Commands
 
- **Build:** `pip install -r requirements.txt && python manage.py migrate`
- **Start:** `gunicorn backend.wsgi:application`
 
## Key Technical Decisions
 
- **ModelViewSet** was used for inventory items to keep the code concise while still providing full CRUD — the router auto-generates all URL patterns.
- **Stock audit log** is handled at the view layer (in `perform_create` and `perform_update`) rather than using Django signals, because it gives more control over the reason categorisation and keeps the logic visible in one place.
- **User isolation** is enforced by filtering the queryset in `get_queryset()`, which means all ViewSet actions (list, retrieve, update, delete) automatically respect user boundaries.
- **Password reset** returns 200 even for non-existent emails to prevent email enumeration attacks.
- **SQLite** is used locally for simplicity, with **PostgreSQL** in production via `dj-database-url` — the switch is handled entirely through the `DATABASE_URL` environment variable.
 
## Use of AI

AI tools were used for research and debugging assistance during development.