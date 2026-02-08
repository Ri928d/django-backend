from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Todo(models.Model):   
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todos')
    name = models.TextField()
    completed = models.BooleanField(default=False)

    def _str_(self):
        return self.name