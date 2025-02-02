from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class Types(models.TextChoices):
        BUSINESS = 'business', 'Business'
        CUSTOMER = 'customer', 'Customer'

    type = models.CharField(max_length=10, choices=Types.choices)
    file = models.ImageField(
        upload_to='profile_pictures/', null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    tel = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    working_hours = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def profile(self):
        if self.type == self.Types.BUSINESS:
            return self.business_profile
        return self.customer_profile

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            if self.type == self.Types.BUSINESS:
                BusinessProfile.objects.create(user=self)
            else:
                CustomerProfile.objects.create(user=self)


class BusinessProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='business_profile')
    file = models.ImageField(
        upload_to='profile_pictures/', null=True, blank=True)
    location = models.CharField(max_length=255)
    tel = models.CharField(max_length=20)
    description = models.TextField()
    working_hours = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Business Profile"


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='customer_profile')
    file = models.ImageField(
        upload_to='profile_pictures/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Customer Profile"
