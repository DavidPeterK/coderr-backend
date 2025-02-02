from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from django_filters import rest_framework as django_filters
from order_app.models import Order
from user_auth_app.models import CustomUser
from .serializers import OrderSerializer
from rest_framework.views import APIView


class OrderFilter(django_filters.FilterSet):
    customer = django_filters.NumberFilter()
    business = django_filters.NumberFilter()
    status = django_filters.ChoiceFilter(choices=Order.STATUS_CHOICES)

    class Meta:
        model = Order
        fields = ['customer', 'business', 'status']


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        django_filters.DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = OrderFilter
    ordering_fields = ['created_at', 'updated_at']

    def get_queryset(self):
        user = self.request.user
        if user.type == 'customer':
            return Order.objects.filter(customer_id=user.id).order_by('-created_at')
        elif user.type == 'business':
            return Order.objects.filter(business_id=user.id).order_by('-created_at')
        return Order.objects.none()

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class OrderDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.type == 'customer':  # String-Vergleich statt Join
            return Order.objects.filter(customer_id=user.id)
        elif user.type == 'business':  # String-Vergleich statt Join
            return Order.objects.filter(business_id=user.id)
        return Order.objects.none()

    def check_object_permissions(self, request, obj):
        user = request.user
        if request.method in ['PUT', 'PATCH']:
            if user.type == 'business' and obj.business_id != user.id:  # ID-Vergleich statt Join
                self.permission_denied(request)
            elif user.type == 'customer' and obj.customer_id != user.id:  # ID-Vergleich statt Join
                self.permission_denied(request)
        return super().check_object_permissions(request, obj)


class OrderDeleteView(generics.DestroyAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAdminUser]


class OrderCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, business_user_id):
        count = Order.objects.filter(
            business_id=business_user_id).count()  # ID-Filter statt Join
        return Response({'count': count})


class CompletedOrderCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, business_user_id):
        count = Order.objects.filter(
            business_id=business_user_id,  # ID-Filter statt Join
            status='completed'
        ).count()
        return Response({'count': count})
