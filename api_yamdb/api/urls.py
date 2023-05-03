from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    api_signup, api_token, UserViewSet, CategoryViewSet,
    CommentViewSet, GenreViewSet, ReviewViewSet, TitleViewSet
)

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews',
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments',
)
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('v1/auth/signup/', api_signup),
    path('v1/auth/token/', api_token),
    path('v1/', include(router_v1.urls)),
    ]
