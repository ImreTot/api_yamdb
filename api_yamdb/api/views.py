from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from reviews.models import Category, Genre, Review, Title
from .filters import TitleFilter
from .mixins import ListCreateDeleteViewSet
from .permissions import IsAdminOrReadOnly
from .serializers import (
    CommentSerializer, CategorySerializer, GenreSerializer,
    ReviewSerializer, TitleBaseSerializer, TitlePostSerializer
)

class CategoryViewSet(ListCreateDeleteViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)

class GenreViewSet(ListCreateDeleteViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)

class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        avg_rating=Avg('reviews__score')).order_by('-avg_rating'
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (
        IsAdminOrReadOnly, IsAuthenticatedOrReadOnly
    )

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return TitlePostSerializer
        return TitleBaseSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для отзывов."""
    serializer_class = ReviewSerializer
    # permission_classes = ()

    def get_title(self):
        id = self.kwargs.get('title_id')
        return get_object_or_404(Title, id=id)

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())

class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментариев."""
    serializer_class = CommentSerializer
    # permission_classes = ()

    def get_review(self):
        id = self.kwargs.get('review_id')
        return get_object_or_404(Review, id=id)

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
