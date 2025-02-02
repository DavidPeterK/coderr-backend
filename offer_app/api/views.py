from rest_framework import generics, permissions, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters import rest_framework as django_filters
from offer_app.models import Offer, OfferDetail
from user_auth_app.models import CustomUser
from offer_app.api.serializers import OfferSerializer, OfferDetailSerializer
from rest_framework.permissions import IsAuthenticated
from user_auth_app.api.permissions import IsOwnerOrAdmin
from rest_framework.exceptions import PermissionDenied


class OfferFilter(django_filters.FilterSet):
    creator = django_filters.NumberFilter(field_name='user')

    class Meta:
        model = Offer
        fields = ['creator']


class OfferListCreateView(generics.ListCreateAPIView):
    serializer_class = OfferSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        django_filters.DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = OfferFilter
    ordering_fields = ['created_at', 'review_count', 'average_rating']

    def get_queryset(self):
        queryset = Offer.objects.all()

        # Preis-Filter über separate Queries
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if min_price:
            offer_ids = OfferDetail.objects.filter(
                price__gte=min_price).values_list('offer_id', flat=True)
            queryset = queryset.filter(id__in=offer_ids)
        if max_price:
            offer_ids = OfferDetail.objects.filter(
                price__lte=max_price).values_list('offer_id', flat=True)
            queryset = queryset.filter(id__in=offer_ids)

        return queryset

    def perform_create(self, serializer):
        if self.request.user.type != 'business':
            raise PermissionDenied(
                "Nur Geschäftsprofile können Angebote erstellen.")
        serializer.save(user=self.request.user)


class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return Offer.objects.filter(user=self.request.user)
        return Offer.objects.all()

    def check_object_permissions(self, request, obj):
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            if obj.user != request.user or request.user.type != CustomUser.Types.BUSINESS:
                self.permission_denied(request)
        return super().check_object_permissions(request, obj)


class OfferDetailSpecificView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            # Separate Query statt Join
            offer_ids = Offer.objects.filter(
                user=self.request.user).values_list('id', flat=True)
            return OfferDetail.objects.filter(offer_id__in=offer_ids)
        return OfferDetail.objects.all()

    def check_object_permissions(self, request, obj):
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            # Separate Query statt Join
            if obj.offer.user_id != request.user.id or request.user.type != CustomUser.Types.BUSINESS:
                self.permission_denied(request)
        return super().check_object_permissions(request, obj)
