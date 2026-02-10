from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import uuid
from django.utils import timezone
from datetime import timedelta

class PasswordResetToken(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def is_valid(self):
        return timezone.now() < self.expires_at
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image_url = models.URLField(blank=True, default="")
    image_public_id = models.CharField(max_length=255, blank=True, default="")

    def save(self, *args, **kwargs):
        if not self.image_url:
            self.image_url = getattr(settings, "DEFAULT_PROFILE_IMAGE_URL", "")
        super().save(*args, **kwargs)

