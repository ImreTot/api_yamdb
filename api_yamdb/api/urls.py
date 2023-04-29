from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.routers import DefaultRouter

from .views import api_signup, api_token

app_name = 'api'

urlpatterns = [
    path('v1/auth/signup/', api_signup),
    path('v1/auth/token/', api_token)
]
