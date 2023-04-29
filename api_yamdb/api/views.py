from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend

from reviews.models import Category, Genre, Title
from .mixins import ListCreateDeleteViewSet
from .filters import TitleFilter
from .permissions import IsAdminOrReadOnly
from .serializers import (
    GenreSerializer, CategorySerializer, 
    TitleBaseSerializer, TitlePostSerializer
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
