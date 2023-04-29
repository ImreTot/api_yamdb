from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from rest_framework import serializers

from reviews.models import Comment, Review, Title, User

class ReviewSerializer(serializers.ModelSerializer):
    """Серилизатор для отзывов."""
    author = serializers.SlugRelatedField(
        queryset=User.objects.all(),        # поправить когда будет модель
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
        queryset=User.objects.all(),        # поправить когда будет модель
        slug_field='username',
    )

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('review', 'author')


class TitlePostSerializer(serializers.ModelSerializer):
    pass


class TitleReadSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(
        source='reviews__score__avg', read_only=True
    )
