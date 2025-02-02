from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from django.http import Http404
from .serializers import (
    CustomerProfileSerializer,
    BusinessProfileSerializer,
    LoginSerializer,
    RegistrationSerializer
)
from user_auth_app.models import CustomUser, BusinessProfile, CustomerProfile


class RegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'type': user.type
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "type": user.type
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_profile(self, user_id=None):
        if user_id is None:
            user = self.request.user
        else:
            user = get_object_or_404(CustomUser, id=user_id)

        if user.type == CustomUser.Types.BUSINESS:
            return get_object_or_404(BusinessProfile, user=user)
        else:
            return get_object_or_404(CustomerProfile, user=user)

    def get_serializer_class(self, profile):
        if isinstance(profile, BusinessProfile):
            return BusinessProfileSerializer
        return CustomerProfileSerializer

    def get(self, request, user_id=None):
        profile = self.get_profile(user_id)
        serializer_class = self.get_serializer_class(profile)
        serializer = serializer_class(profile)
        data = serializer.data

        # Flache Struktur für das Frontend
        if 'user' in data:
            user_data = data.pop('user')
            data.update(user_data)
            data['user'] = user_data['pk']  # Nur die ID für Redirects

        return Response(data)

    def patch(self, request, user_id=None):
        profile = self.get_profile(user_id)
        serializer_class = self.get_serializer_class(profile)
        serializer = serializer_class(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            data = serializer.data

            # Auch hier flache Struktur und ID
            if 'user' in data:
                user_data = data.pop('user')
                data.update(user_data)
                data['user'] = user_data['pk']

            return Response(data)
        return Response(serializer.errors, status=400)


class BusinessProfileListView(generics.ListAPIView):
    serializer_class = BusinessProfileSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return BusinessProfile.objects.select_related('user').filter(
            user__type=CustomUser.Types.BUSINESS
        )


class CustomerProfileListView(generics.ListAPIView):
    serializer_class = CustomerProfileSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return CustomerProfile.objects.select_related('user').filter(
            user__type=CustomUser.Types.CUSTOMER
        )
