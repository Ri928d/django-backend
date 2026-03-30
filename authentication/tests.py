
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Profile, PasswordResetToken


class RegisterAPITest(TestCase):
    """Tests for user registration endpoint."""

    def setUp(self):
        self.client = APIClient()

    def test_register_success(self):
        """Test successful user registration returns tokens."""
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "strongpass123!",
        }
        response = self.client.post("/api/auth/register/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_creates_profile(self):
        """Test that registration automatically creates a user profile."""
        data = {
            "username": "profileuser",
            "email": "profile@example.com",
            "password": "strongpass123!",
        }
        self.client.post("/api/auth/register/", data, format="json")
        user = User.objects.get(username="profileuser")
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_register_duplicate_username(self):
        """Test that duplicate username is rejected."""
        User.objects.create_user(
            username="existing", email="a@example.com", password="pass123!"
        )
        data = {
            "username": "existing",
            "email": "b@example.com",
            "password": "strongpass123!",
        }
        response = self.client.post("/api/auth/register/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email(self):
        """Test that duplicate email is rejected."""
        User.objects.create_user(
            username="user1", email="taken@example.com", password="pass123!"
        )
        data = {
            "username": "user2",
            "email": "taken@example.com",
            "password": "strongpass123!",
        }
        response = self.client.post("/api/auth/register/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_weak_password(self):
        """Test that a weak/short password is rejected."""
        data = {
            "username": "weakuser",
            "email": "weak@example.com",
            "password": "123",
        }
        response = self.client.post("/api/auth/register/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_fields(self):
        """Test that missing required fields fail validation."""
        response = self.client.post(
            "/api/auth/register/", {"username": "incomplete"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginAPITest(TestCase):
    """Tests for JWT token authentication."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="loginuser", email="login@example.com", password="loginpass123!"
        )

    def test_login_success(self):
        """Test successful login returns access and refresh tokens."""
        data = {"username": "loginuser", "password": "loginpass123!"}
        response = self.client.post("/api/auth/token/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_wrong_password(self):
        """Test that wrong password returns 401."""
        data = {"username": "loginuser", "password": "wrongpassword"}
        response = self.client.post("/api/auth/token/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        """Test that nonexistent user returns 401."""
        data = {"username": "ghost", "password": "somepass123!"}
        response = self.client.post("/api/auth/token/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        """Test that a valid refresh token returns a new access token."""
        login_response = self.client.post(
            "/api/auth/token/",
            {"username": "loginuser", "password": "loginpass123!"},
            format="json",
        )
        refresh_token = login_response.data["refresh"]
        response = self.client.post(
            "/api/auth/token/refresh/",
            {"refresh": refresh_token},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)


class ProfileAPITest(TestCase):
    """Tests for user profile endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="profuser", email="prof@example.com", password="profpass123!"
        )
        Profile.objects.get_or_create(user=self.user)
        response = self.client.post(
            "/api/auth/token/",
            {"username": "profuser", "password": "profpass123!"},
            format="json",
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )

    def test_get_profile(self):
        """Test retrieving the authenticated user's profile."""
        response = self.client.get("/api/auth/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "profuser")
        self.assertEqual(response.data["email"], "prof@example.com")

    def test_update_profile_email(self):
        """Test updating the user email through profile endpoint."""
        response = self.client.patch(
            "/api/auth/profile/",
            {"email": "updated@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "updated@example.com")
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "updated@example.com")

    def test_update_profile_image(self):
        """Test updating the profile image URL."""
        response = self.client.patch(
            "/api/auth/profile/",
            {"image_url": "https://example.com/photo.jpg"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["image_url"], "https://example.com/photo.jpg")

    def test_profile_unauthenticated(self):
        """Test that unauthenticated users cannot access the profile."""
        client = APIClient()
        response = client.get("/api/auth/profile/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PasswordResetModelTest(TestCase):
    """Tests for the PasswordResetToken model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="resetuser", email="reset@example.com", password="resetpass123!"
        )

    def test_create_token(self):
        """Test creating a password reset token."""
        token = PasswordResetToken.objects.create(user=self.user)
        self.assertIsNotNone(token.token)
        self.assertIsNotNone(token.expires_at)
        self.assertTrue(token.is_valid())

    def test_token_uniqueness(self):
        """Test that each generated token is unique."""
        token1 = PasswordResetToken.objects.create(user=self.user)
        token2 = PasswordResetToken.objects.create(user=self.user)
        self.assertNotEqual(token1.token, token2.token)


class PasswordResetAPITest(TestCase):
    """Tests for password reset API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="resetapi", email="resetapi@example.com", password="oldpass123!"
        )

    def test_request_reset_existing_email(self):
        """Test requesting reset for existing email returns 200."""
        response = self.client.post(
            "/api/auth/password-reset/",
            {"email": "resetapi@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_request_reset_nonexistent_email(self):
        """Test requesting reset for nonexistent email still returns 200 for security."""
        response = self.client.post(
            "/api/auth/password-reset/",
            {"email": "nonexistent@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_confirm_reset_with_valid_token(self):
        """Test that a valid token allows password reset."""
        token_obj = PasswordResetToken.objects.create(user=self.user)
        response = self.client.post(
            "/api/auth/password-reset-confirm/",
            {"token": str(token_obj.token), "new_password": "newstrongpass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newstrongpass123!"))

    def test_confirm_reset_invalid_token(self):
        """Test that an invalid token is rejected."""
        response = self.client.post(
            "/api/auth/password-reset-confirm/",
            {"token": "invalid-token-12345", "new_password": "newpass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_deleted_after_use(self):
        """Test that the token is removed after a successful password reset."""
        token_obj = PasswordResetToken.objects.create(user=self.user)
        token_str = str(token_obj.token)
        self.client.post(
            "/api/auth/password-reset-confirm/",
            {"token": token_str, "new_password": "newstrongpass123!"},
            format="json",
        )
        self.assertFalse(
            PasswordResetToken.objects.filter(token=token_str).exists()
        )