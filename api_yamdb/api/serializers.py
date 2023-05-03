from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from rest_framework import serializers, status
from rest_framework.validators import UniqueValidator
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils import timezone

from reviews.models import (Comment, Review, Title,
                            Category, Genre)
CHOICES = ['user', 'moderator', 'admin']

MAX_EMAIL_LENGTH = 254
MAX_USERNAME_LENGTH = 150

User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    queryset = User.objects.all()
    username = serializers.RegexField(
        validators=[UniqueValidator(queryset=queryset),],
        regex=r'^[\w.@+-]',
        required=True
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=queryset),],
        required=True
    )

    def validate_username(self, value):
        """Функция проверяет, что username - не 'me'
        вне зависимости от регистра, а также не длиннее 150 символов."""
        if value.lower() == 'me' or len(value) > MAX_USERNAME_LENGTH:
            raise serializers.ValidationError('invalid username')
        return value

    def validate_email(self, value):
        """Функция проверяет, что email не длиннее 254 символов."""
        if len(value) > MAX_EMAIL_LENGTH:
            raise serializers.ValidationError('email is too long.')
        return value

    class Meta:
        model = User
        fields = ('username', 'email',)


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=MAX_USERNAME_LENGTH
    )
    confirmation_code = serializers.CharField(
        required=True,
    )

    class Meta:
        fields = ('username', 'confirmation_code')


class UserIsAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                  'bio', 'role')

    def validate_role(self, value):
        if value not in ['user', 'moderator', 'admin']:
            raise status.HTTP_400_BAD_REQUEST
        return value


class UserSerializer(serializers.ModelSerializer):
    role = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                  'bio', 'role')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('id',)
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ('id',)
        lookup_field = 'slug'


class TitleBaseSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(
        source='reviews__score__avg', read_only=True
    )
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class TitlePostSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True, slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        many=True, slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year',
            'description', 'genre', 'category'
        )

    def validate_year(self, value):
        current_year = timezone.now().year
        if value > current_year:
            raise serializers.ValidationError(
                'Произведение еще не написали. Вы указали будующий год.'
            )
        if value < 0:
            raise serializers.ValidationError(
                'Год не может быть отрицательным.'
            )
        return value


class ReviewSerializer(serializers.ModelSerializer):
    """Серилизатор для отзывов."""
    author = serializers.SlugRelatedField(
        queryset=User.objects.all(),  # поправить когда будет модель
        slug_field='username'
    )
    score = serializers.IntegerField(required=True)

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('title', 'author')

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        if (
                request.method == "POST"
                and title.reviews.filter(title=title_id, author=author).exists()
        ):
            raise ValidationError('Вы уже оставляли отзыв!')
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Серилизатор для комментариев."""
    author = serializers.SlugRelatedField(
        queryset=User.objects.all(),  # поправить когда будет модель
        slug_field='username',
    )

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('review', 'author')
