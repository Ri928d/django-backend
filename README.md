# Django Todo Backend API

A RESTful API built with Django and Django REST Framework for a todo application with JWT authentication. This is an ongoing project demonstrating how to set up a full-stack application with authentication and CRUD operations.

> **Note:** This is a learning project and an example for students. It demonstrates best practices for setting up Django backends with authentication, but is not meant to be production-perfect code.

## 🚀 Live Demo

The backend is deployed on Render and accessible at:
**https://django-backend-aqrl.onrender.com**

⚠️ **Important:** The free tier on Render spins down after inactivity. The first request may take up to **1 minute** to start up. Please be patient!

### Testing the Live API

The easiest way to test the API is using the **interactive Swagger documentation**:

👉 **Visit:** https://django-backend-aqrl.onrender.com/api/docs/

Swagger provides a user-friendly interface to test all endpoints directly in your browser. You can also use tools like Postman or cURL if you prefer.

### Frontend Repository

The frontend React application is available at:
**https://github.com/anandveeraswamy/moz-todo-react**

Frontend deployment: https://moz-todo-react.onrender.com

## 📋 Features

### Authentication
- **User Registration** - Create new user accounts
- **JWT Authentication** - Secure token-based authentication
- **Login/Logout** - Session management with access and refresh tokens
- **Password Reset** - Email-based password reset flow (via SendGrid)
- **User Profile** - View and update user profile with Cloudinary image uploads

### Todo CRUD Operations
- **Create** - Add new todos
- **Read** - List all todos for authenticated user
- **Update** - Mark todos as complete/incomplete, edit todo text
- **Delete** - Remove todos
- **Filter** - Todos are user-specific (each user sees only their todos)

### API Documentation
- **Swagger UI** - Interactive API documentation at `/api/docs/`
- **OpenAPI Schema** - Machine-readable schema at `/api/schema/`

## 🛠️ Tech Stack

- **Django 6.0.2** - Python web framework
- **Django REST Framework** - API toolkit
- **Simple JWT** - JWT authentication
- **PostgreSQL** - Production database (via Render)
- **SQLite** - Local development database
- **SendGrid** - Email service for password resets
- **Cloudinary** - Image hosting for profile pictures
- **drf-spectacular** - OpenAPI schema generation
- **CORS Headers** - Cross-origin resource sharing

## 📁 Project Structure

```
django-todo-backend/
├── authentication/           # User authentication app
│   ├── models.py            # PasswordResetToken, Profile models
│   ├── serializers.py       # User, Profile serializers
│   ├── views.py             # Auth endpoints
│   └── urls.py              # Auth routes
├── backend/                 # Project settings
│   ├── settings.py          # Configuration
│   ├── urls.py              # Main URL routing
│   └── wsgi.py              # WSGI config for deployment
├── todo/                    # Todo app
│   ├── models.py            # Todo model
│   ├── serializers.py       # Todo serializer
│   ├── views.py             # Todo CRUD views
│   └── admin.py             # Django admin configuration
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
└── db.sqlite3              # Local SQLite database (gitignored)
```

## 🚀 Local Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd django-todo-backend
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

Create a `.env` file in the `django-todo-backend` directory:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
FRONTEND_URL=http://localhost:3000
DEFAULT_PROFILE_IMAGE_URL=https://via.placeholder.com/150

# Optional - for password reset emails
SENDGRID_API_KEY=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=your-email@example.com

# Optional - for profile image uploads
VITE_CLOUDINARY_CLOUD_NAME=your-cloudinary-name
VITE_CLOUDINARY_UPLOAD_PRESET=your-upload-preset
```

> **Note:** For local development, you don't need SendGrid or Cloudinary. The app will work without them, but password reset and profile image upload won't function.

### Step 5: Run Migrations

```bash
python manage.py migrate
```

This creates the SQLite database and all necessary tables.

### Step 6: Create a Superuser (Optional)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account. You can then access the Django admin at `http://localhost:8000/admin/`

### Step 7: Run the Development Server

```bash
python manage.py runserver
```

The API will be available at:
- **API Base:** http://localhost:8000/api/
- **Admin Panel:** http://localhost:8000/admin/
- **API Docs (Swagger):** http://localhost:8000/api/docs/

You can now test all endpoints using the Swagger UI at http://localhost:8000/api/docs/

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register/` | Register new user | No |
| POST | `/api/auth/token/` | Login (get JWT tokens) | No |
| POST | `/api/auth/token/refresh/` | Refresh access token | No |
| POST | `/api/auth/password-reset/` | Request password reset | No |
| POST | `/api/auth/password-reset-confirm/` | Confirm password reset | No |
| GET | `/api/auth/profile/` | Get user profile | Yes |
| PATCH | `/api/auth/profile/` | Update user profile | Yes |

### Todos

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/todos/` | List all user's todos | Yes |
| POST | `/api/todos/` | Create new todo | Yes |
| GET | `/api/todos/{id}/` | Get specific todo | Yes |
| PUT | `/api/todos/{id}/` | Update todo | Yes |
| PATCH | `/api/todos/{id}/` | Partially update todo | Yes |
| DELETE | `/api/todos/{id}/` | Delete todo | Yes |

### Documentation

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/docs/` | Swagger UI |
| GET | `/api/schema/` | OpenAPI schema |

## 🗄️ Database

### Local Development
- Uses **SQLite** (`db.sqlite3`)
- No setup required
- File-based, perfect for development

### Production (Render)
- Uses **PostgreSQL**
- Configured via `DATABASE_URL` environment variable
- Automatically provisioned by Render

### Resetting Local Database

If you need to start fresh:

```bash
# Delete database
rm db.sqlite3

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## 🧪 Testing

### Using Swagger UI

1. Start the server: `python manage.py runserver`
2. Visit http://localhost:8000/api/docs/ for interactive API testing
3. Use the "Try it out" button on any endpoint to test it directly in your browser
4. For authenticated endpoints, click "Authorize" and enter your JWT token

### Django Shell

For direct database queries:

```bash
python manage.py shell
```

```python
# Inside shell
from django.contrib.auth.models import User
from todo.models import Todo

# Get all users
User.objects.all()

# Get all todos
Todo.objects.all()

# Create a todo
user = User.objects.first()
Todo.objects.create(user=user, name="Test todo", completed=False)
```

## 🌐 Deployment (Render)

This project is deployed on Render. Here's how it's configured:

### Environment Variables on Render

```
DEBUG=False
SECRET_KEY=<production-secret-key>
DATABASE_URL=<postgres-connection-string>
FRONTEND_URL=https://your-frontend.onrender.com
SENDGRID_API_KEY=<your-sendgrid-key>
DEFAULT_FROM_EMAIL=<your-email>
DEFAULT_PROFILE_IMAGE_URL=<cloudinary-url>
```

### Build Command

```bash
pip install -r requirements.txt && python manage.py migrate
```

### Start Command

```bash
gunicorn backend.wsgi:application
```

## 📝 Common Issues & Solutions

### Issue: "No module named 'module_name'"
**Solution:** Make sure virtual environment is activated and dependencies are installed
```bash
pip install -r requirements.txt
```

### Issue: "Database table doesn't exist"
**Solution:** Run migrations
```bash
python manage.py migrate
```

### Issue: "CORS error in browser"
**Solution:** Check `CORS_ALLOWED_ORIGINS` in `settings.py` includes your frontend URL

### Issue: "401 Unauthorized on protected endpoints"
**Solution:** Make sure you're including the JWT token in the Authorization header

### Issue: Render site taking forever to load
**Solution:** Free tier spins down after inactivity. Wait ~1 minute for first request.

## 📚 Learning Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [JWT Authentication](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Render Deployment Guide](https://render.com/docs/deploy-django)

## 🤝 For Students

This project demonstrates:
- ✅ RESTful API design
- ✅ JWT authentication implementation
- ✅ CRUD operations
- ✅ Database migrations
- ✅ Environment configuration
- ✅ API documentation
- ✅ Deployment to production

**What you can learn:**
1. How to structure a Django REST API
2. How to implement secure authentication
3. How to create CRUD endpoints
4. How to deploy to a cloud platform
5. How to document your API


## 📄 License

This is a student learning project. Feel free to use it as a reference for your own projects.

## 🐛 Known Issues

- Password reset requires SendGrid configuration
- Profile image upload requires Cloudinary setup
- Free Render tier has cold start delays (~1 min)
- SQLite used for local dev, PostgreSQL for production (different behaviors possible)

---

**Happy Coding! 🚀**
