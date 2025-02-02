from django.db import models
from django.conf import settings
from offer_app.models import OfferDetail


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_orders',
        null=True
    )
    business = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='business_orders',
        null=True
    )
    offer_detail = models.ForeignKey(
        OfferDetail,
        on_delete=models.CASCADE,
        related_name='orders',
        null=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        offer_title = self.offer_detail.offer.title if self.offer_detail and hasattr(
            self.offer_detail, 'offer') else 'No Offer'
        return f"Order {self.id} - {offer_title} ({self.status})"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.customer and hasattr(self.customer, 'type') and self.customer.type != 'customer':
            raise ValidationError('Nur Kunden können Bestellungen aufgeben')
        if self.business and hasattr(self.business, 'type') and self.business.type != 'business':
            raise ValidationError(
                'Bestellungen können nur an Business-User gehen')
