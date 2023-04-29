from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .serializers import SignupSerializer, TokenSerializer

User = get_user_model()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'token': str(refresh.access_token)
    }


@api_view(['POST'])
def api_signup(request):
    """
    Функция первичной самостоятельной регистрации пользователя
    принимает только POST-запросы по следующему шаблону:
    {
        "username": "string",
        "email": "string"
    }
    default_token_generator() на основе объекта класса User создает токен,
    который send_mail() отправляет на почту по указанному в запросе адресу
    """
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        username = request.data['username']
        email = request.data['email']
        user = get_object_or_404(User, username=username)
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            'Подтверждение регистрации на сайте YaMDB',
            'Здравствуйте!\nВы зарегистрировались на сайте YaMDB, '
            f'оставив username - {username} и email - {email}. '
            'Чтобы завершить регистрацию, введите код подтверждения - '
            f'{confirmation_code}',
            'admin@YaMDB.ru',
            [email]
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def api_token(request):
    """Функция первичной самостоятельной регистрации пользователя
    принимает только POST-запросы по следующему шаблону:
    {
        "username": "string",
        "confirmation_code": "string"
    }
    Возвращает JWT-токен
    """
    confirmation_code = request.data['confirmation_code']
    username = request.data['username']
    user = User.objects.get(username=username)
    if default_token_generator.check_token(user, confirmation_code):
        token = get_tokens_for_user(user)
        serializer = TokenSerializer(data=token)
        return Response(serializer.initial_data, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)
