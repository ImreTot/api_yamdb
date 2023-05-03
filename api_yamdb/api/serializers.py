from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from rest_framework import serializers, status
from django.db.models import Avg
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
        fields = ('name', 'slug')
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ('id',)
        lookup_field = 'slug'


class TitleBaseSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.SerializerMethodField()

    # https://django.fun/ru/docs/django/4.1/topics/db/aggregation/#:~:text=%23%20Total%20number%20of%20books%20with%20publisher%3DBaloneyPress%0A%3E%3E%3E%20Book.objects.filter(publisher__name%3D%27BaloneyPress%27).count()%0A73%0A%0A%23%20Average%20price%20across%20all%20books.%0A%3E%3E%3E%20from%20django.db.models%20import%20Avg%0A%3E%3E%3E%20Book.objects.aggregate(Avg(%27price%27))%0A%7B%27price__avg%27%3A%2034.35%7D
    def get_rating(self, obj):
        avg = Review.objects.filter(title=obj.id).aggregate(Avg('score'))
        return avg['score__avg']

    class Meta:
        model = Title
        fields = '__all__'


class TitlePostSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True, slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
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
        slug_field='username',
        read_only=True,
    )

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
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('review', 'author')
