from rest_framework import serializers
from offer_app.models import Offer, OfferDetail
from user_auth_app.api.serializers import UserBasicSerializer
from user_auth_app.models import CustomUser


class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions',
                  'delivery_time_in_days', 'price', 'features', 'offer_type']


class OfferSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    details = OfferDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Offer
        fields = ['id', 'user', 'review_count', 'average_rating', 'title', 'image', 'description',
                  'created_at', 'updated_at', 'details']
        read_only_fields = ['user', 'review_count',
                            'average_rating', 'created_at', 'updated_at']

    def validate(self, data):
        if self.context['request'].user.type != 'business':
            raise serializers.ValidationError(
                'Nur Business-User können Angebote erstellen')
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        if user.type != 'business':
            raise serializers.ValidationError(
                'Nur Business-User können Angebote erstellen')
        validated_data['user'] = user
        return super().create(validated_data)

    def validate_details(self, value):
        if len(value) != 3:
            raise serializers.ValidationError(
                "Es müssen genau drei Angebotsdetails (basic, standard, premium) vorhanden sein.")
        types = [detail['offer_type'] for detail in value]
        if sorted(types) != ['basic', 'premium', 'standard']:
            raise serializers.ValidationError(
                "Angebotsdetails müssen die Typen basic, standard und premium enthalten.")
        return value

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        if details_data:
            instance.details.all().delete()
            for detail_data in details_data:
                OfferDetail.objects.create(offer=instance, **detail_data)
        return instance
