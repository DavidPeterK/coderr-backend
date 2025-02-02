from user_auth_app.models import CustomUser, BusinessProfile, CustomerProfile
from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({
                "password": ["Das Passwort ist nicht gleich mit dem wiederholten Passwort."]
            })
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({
                "email": ["Diese E-Mail-Adresse wird bereits verwendet."]
            })
        return data

    def create(self, validated_data):
        validated_data.pop('repeated_password')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            type=validated_data['type'],
        )
        Token.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            data['user'] = user
            return data
        raise serializers.ValidationError({
            "detail": ["Ungültige Anmeldeinformationen."]
        })


class UserSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(source='id')

    class Meta:
        model = CustomUser
        fields = ['pk', 'username', 'email', 'type']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='*')

    class Meta:
        model = CustomUser
        fields = ['user', 'location', 'tel',
                  'description', 'working_hours', 'file']


class UserBasicSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(source='id')

    class Meta:
        model = CustomUser
        fields = ['pk', 'username', 'first_name',
                  'last_name', 'email', 'created_at']

    def to_representation(self, instance):
        # Wenn das Feld als einzelner Wert verwendet wird (z.B. für IDs)
        if self.parent is None:
            return instance.id
        # Ansonsten das vollständige Objekt
        return super().to_representation(instance)


class BusinessProfileSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    type = serializers.SerializerMethodField()

    class Meta:
        model = BusinessProfile
        fields = ['user', 'file', 'location', 'tel',
                  'description', 'working_hours', 'type']

    def get_type(self, obj):
        return obj.user.type if obj.user else None


class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    type = serializers.SerializerMethodField()
    uploaded_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')
    created_at = serializers.DateTimeField(source='user.created_at')

    class Meta:
        model = CustomerProfile
        fields = ['user', 'file', 'uploaded_at', 'type',
                  'first_name', 'last_name', 'username', 'email', 'created_at']

    def get_type(self, obj):
        return obj.user.type if obj.user else None

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        # Update user fields
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()
        # Update profile fields
        return super().update(instance, validated_data)
