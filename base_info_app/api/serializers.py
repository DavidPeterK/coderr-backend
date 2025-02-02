from rest_framework import serializers
from base_info_app.models import Review
from user_auth_app.api.serializers import UserBasicSerializer
from offer_app.api.serializers import OfferSerializer


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = UserBasicSerializer(read_only=True)
    business_user = UserBasicSerializer(read_only=True)
    offer = OfferSerializer(read_only=True)
    reviewer_id = serializers.IntegerField(write_only=True, required=False)
    business_user_id = serializers.IntegerField(
        write_only=True, required=False)
    offer_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Review
        fields = [
            'id',
            'reviewer',
            'business_user',
            'offer',
            'reviewer_id',
            'business_user_id',
            'offer_id',
            'rating',
            'comment',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['reviewer', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context['request']
        user = request.user

        if user.type != 'customer':
            raise serializers.ValidationError(
                'Nur Kunden können Bewertungen abgeben')

        validated_data['reviewer_id'] = user.id

        offer = validated_data.get('offer')
        if offer:
            validated_data['business_user_id'] = offer.user_id

        return super().create(validated_data)

    def validate(self, data):
        request = self.context.get('request')
        if request and request.user.type != 'customer':
            raise serializers.ValidationError(
                'Nur Kunden können Bewertungen abgeben')
        return data
