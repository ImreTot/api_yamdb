from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    queryset = User.objects.all()
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=queryset)]
    )
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=queryset)]
    )

    class Meta:
        model = User
        fields = ('username', 'email',)


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(read_only=True)

    class Meta:
        fields = ('token',)
