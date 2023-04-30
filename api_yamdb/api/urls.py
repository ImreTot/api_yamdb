from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import api_signup, api_token, UserViewSet

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('v1/auth/signup/', api_signup),
    path('v1/auth/token/', api_token),
    path('v1/', include(router_v1.urls))
]
