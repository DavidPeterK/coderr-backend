from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    PROFILE_TYPE_CHOICES = [
        ('business', 'Business'),
        ('customer', 'Customer'),
    ]
    type = models.CharField(max_length=10, choices=PROFILE_TYPE_CHOICES)

    def __str__(self):
        return self.username
