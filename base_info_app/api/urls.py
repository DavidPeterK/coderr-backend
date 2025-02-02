from django.urls import path
from .views import BaseInfoView, ReviewListView

urlpatterns = [
    path('base-info/', BaseInfoView.as_view(), name='base-info'),
    path('reviews/', ReviewListView.as_view(), name='review-list'),
]
