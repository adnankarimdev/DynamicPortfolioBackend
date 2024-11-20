from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Create your models here.
class CustomUser(AbstractUser):
    # Only keeping email and password
    email = models.EmailField(unique=True)
    data = models.JSONField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    url_hidden = models.BooleanField(default=False)
    
    # Set the USERNAME_FIELD to email since you want users to log in with email instead of the username
    USERNAME_FIELD = "email"
    
    # No additional required fields, as only email and password are needed
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email