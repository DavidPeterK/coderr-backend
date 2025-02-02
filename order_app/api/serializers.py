from rest_framework import serializers
from order_app.models import Order
from user_auth_app.api.serializers import UserBasicSerializer
from offer_app.api.serializers import OfferDetailSerializer
from offer_app.models import OfferDetail
from user_auth_app.models import CustomUser


class OrderSerializer(serializers.ModelSerializer):
    customer = UserBasicSerializer(source='customer_user', read_only=True)
    business = UserBasicSerializer(source='business_user', read_only=True)
    offer_detail = OfferDetailSerializer(read_only=True)
    features = serializers.JSONField(
        source='offer_detail.features', read_only=True)
    title = serializers.CharField(source='offer_detail.title', read_only=True)
    delivery_time_in_days = serializers.IntegerField(
        source='offer_detail.delivery_time_in_days', read_only=True)
    revisions = serializers.IntegerField(
        source='offer_detail.revisions', read_only=True)
    price = serializers.DecimalField(
        source='offer_detail.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'customer',
            'business',
            'customer_user',  # Für Frontend-Redirects
            'business_user',  # Für Frontend-Redirects
            'offer_detail',
            'status',
            'created_at',
            'updated_at',
            'features',
            'title',
            'delivery_time_in_days',
            'revisions',
            'price'
        ]
        read_only_fields = ['customer', 'business', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context['request']
        user = request.user

        if user.type != 'customer':
            raise serializers.ValidationError(
                'Nur Kunden können Bestellungen aufgeben')

        validated_data['customer_id'] = user.id

        offer_detail = validated_data.get('offer_detail')
        if offer_detail:
            validated_data['business_id'] = offer_detail.offer.user_id

        return super().create(validated_data)

    def validate(self, data):
        if self.context['request'].method in ['PUT', 'PATCH']:
            if 'status' in data and self.context['request'].user.type != 'business':
                raise serializers.ValidationError(
                    'Nur Business-User können den Status ändern')
        return data


class OrderCreateSerializer(serializers.Serializer):
    offer_detail_id = serializers.IntegerField()

    def validate_offer_detail_id(self, value):
        try:
            offer_detail = OfferDetail.objects.get(id=value)
            return offer_detail
        except OfferDetail.DoesNotExist:
            raise serializers.ValidationError("Offer detail not found.")

    def create(self, validated_data):
        customer_user = self.context['request'].user
        offer_detail = validated_data['offer_detail_id']
        return Order.objects.create(
            customer_user=customer_user,
            business_user=offer_detail.offer.user,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type
        )
