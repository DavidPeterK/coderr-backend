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
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            raise serializers.ValidationError({
                "detail": ["Bitte geben Sie sowohl den Benutzernamen als auch das Passwort an."]
            })

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError({
                "detail": ["Ungültige Anmeldeinformationen."]
            })

        data['user'] = user
        return data
