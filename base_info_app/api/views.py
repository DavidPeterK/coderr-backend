from rest_framework import generics, filters, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters import rest_framework as django_filters
from django.db.models import Avg, Sum
from offer_app.models import Offer
from user_auth_app.models import CustomUser
from .serializers import ReviewSerializer
from base_info_app.models import Review


class BaseInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # Separate Queries statt Joins
        review_count = Review.objects.count()
        average_rating = Review.objects.aggregate(avg_rating=Avg('rating'))[
            'avg_rating'] or 0.0
        average_rating = round(average_rating, 1)
        business_count = CustomUser.objects.filter(
            type='business').count()  # String-Vergleich statt Join
        offer_count = Offer.objects.count()

        return Response({
            "review_count": review_count,
            "average_rating": average_rating,
            "business_profile_count": business_count,
            "offer_count": offer_count,
        })


class ReviewFilter(django_filters.FilterSet):
    reviewer = django_filters.NumberFilter(field_name='reviewer_id')
    business = django_filters.NumberFilter(field_name='business_user_id')
    offer = django_filters.NumberFilter(field_name='offer_id')

    class Meta:
        model = Review
        fields = ['reviewer', 'business', 'offer']


class ReviewListView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        django_filters.DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ['created_at', 'updated_at', 'rating']

    def get_queryset(self):
        queryset = Review.objects.all()

        # Filter für Profil-Reviews
        reviewer_id = self.request.query_params.get('reviewer')
        business_id = self.request.query_params.get('business')

        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)
        if business_id:
            queryset = queryset.filter(business_user_id=business_id)

        return queryset.order_by('-updated_at')

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response([])  # Leere Liste bei Fehlern zurückgeben
