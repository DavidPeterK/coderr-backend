from django.db import models
from django.conf import settings
from offer_app.models import Offer


class Review(models.Model):
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='written_reviews',
        null=True
    )
    business_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_reviews',
        null=True
    )
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name='reviews',
        null=True
    )
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        reviewer_name = self.reviewer.username if self.reviewer else 'Unknown'
        business_name = self.business_user.username if self.business_user else 'Unknown'
        return f"Review by {reviewer_name} for {business_name}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.reviewer and hasattr(self.reviewer, 'type') and self.reviewer.type != 'customer':
            raise ValidationError('Nur Kunden können Bewertungen abgeben')
        if self.business_user and hasattr(self.business_user, 'type') and self.business_user.type != 'business':
            raise ValidationError(
                'Bewertungen können nur für Business-User abgegeben werden')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
