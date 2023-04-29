from django.urls import path

from .views import api_signup, api_token

app_name = 'api'

urlpatterns = [
    path('v1/auth/signup/', api_signup),
    path('v1/auth/token/', api_token)
]
