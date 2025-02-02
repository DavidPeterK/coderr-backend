from django.urls import path
from .views import OfferListCreateView, OfferDetailView, OfferDetailSpecificView

urlpatterns = [
    path('offers/', OfferListCreateView.as_view(), name='offer-list'),
    path('offers/<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
    path('offer-details/<int:pk>/', OfferDetailSpecificView.as_view(),
         name='offer-detail-specific'),
]
