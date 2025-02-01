from rest_framework import generics, permissions
from offer_app.models import Offer, OfferDetail
from offer_app.api.serializers import OfferSerializer, OfferDetailSerializer
from rest_framework.permissions import IsAuthenticated
from user_auth_app.api.permissions import IsOwnerOrAdmin


from rest_framework.exceptions import PermissionDenied


class OfferListView(generics.ListCreateAPIView):
    serializer_class = OfferSerializer
    queryset = Offer.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset
        creator_id = self.request.query_params.get('creator_id')
        min_price = self.request.query_params.get('min_price')
        max_delivery_time = self.request.query_params.get('max_delivery_time')
        search = self.request.query_params.get('search')
        ordering = self.request.query_params.get('ordering', 'updated_at')

        if creator_id:
            queryset = queryset.filter(user_id=creator_id)
        if min_price:
            queryset = queryset.filter(details__price__gte=min_price)
        if max_delivery_time:
            queryset = queryset.filter(
                details__delivery_time_in_days__lte=max_delivery_time)
        if search:
            queryset = queryset.filter(title__icontains=search) | queryset.filter(
                description__icontains=search)

        return queryset.order_by(ordering)

    def perform_create(self, serializer):
        if self.request.user.type != 'business':
            raise PermissionDenied(
                "Nur Geschäftsprofile können Angebote erstellen.")

        serializer.save(user=self.request.user)


class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OfferSerializer
    queryset = Offer.objects.all()
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsOwnerOrAdmin()]
        return super().get_permissions()


class OfferDetailSpecificView(generics.RetrieveAPIView):
    serializer_class = OfferDetailSerializer
    queryset = OfferDetail.objects.all()
    permission_classes = [IsAuthenticated]
