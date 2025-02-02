from django.urls import path
from .views import (
    UserProfileView,
    BusinessProfileListView,
    CustomerProfileListView,
    RegistrationView,
    LoginView,
)

urlpatterns = [
    # Auth URLs
    path('login/', LoginView.as_view(), name='login'),
    path('registration/', RegistrationView.as_view(), name='register'),

    # Profile URLs
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/<int:user_id>/', UserProfileView.as_view(), name='profile-detail'),
    path('profiles/business/', BusinessProfileListView.as_view(),
         name='business-profiles'),
    path('profiles/customer/', CustomerProfileListView.as_view(),
         name='customer-profiles'),
]
