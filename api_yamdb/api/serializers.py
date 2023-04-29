from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email',)


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(read_only=True)

    class Meta:
        fields = ('token',)

    def validate(self, attrs):
        ...
