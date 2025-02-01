from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from base_info_app.api import serializers
from order_app import models
from order_app.models import Order
from .serializers import OrderSerializer, OrderCreateSerializer
from django.db.models import Q


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(
            models.Q(customer_user=user) | models.Q(business_user=user)
        )


class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.type != 'customer':
            raise serializers.ValidationError(
                "Only customers can create orders.")
        serializer.save()


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]


class OrderUpdateView(generics.UpdateAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if 'status' in request.data:
            instance.status = request.data['status']
            instance.save()
        return Response(self.get_serializer(instance).data)


class OrderDeleteView(generics.DestroyAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [IsAdminUser]


class OrderCountView(generics.GenericAPIView):
    def get(self, request, business_user_id, *args, **kwargs):
        count = Order.objects.filter(
            business_user_id=business_user_id, status='in_progress').count()
        return Response({"order_count": count})


class CompletedOrderCountView(generics.GenericAPIView):
    def get(self, request, business_user_id, *args, **kwargs):
        count = Order.objects.filter(
            business_user_id=business_user_id, status='completed').count()
        return Response({"completed_order_count": count})
