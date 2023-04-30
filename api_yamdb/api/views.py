from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .serializers import (SignupSerializer, TokenSerializer,
                          UserSerializer)
from .validators import is_username_not_me
from .permissions import IsAdmin

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
    который send_mail() отправляет на почту по указанному в запросе адресу.
    Отправленные письма хранятся в папке sent_emails.
    """
    serializer = SignupSerializer(data=request.data)
    username = is_username_not_me(request.data['username'])
    if serializer.is_valid():
        serializer.save()
        user = get_object_or_404(User, username=username)
        confirmation_code = default_token_generator.make_token(user)
        email = request.data['email']
        letter_header = 'Подтверждение регистрации на сайте YaMDB'
        letter_message = (f'Здравствуйте!\n'
                          f'Вы зарегистрировались на сайте YaMDB, '
                          f'оставив username - {username} '
                          f'и email - {email}.\n'
                          f'Чтобы завершить регистрацию, '
                          f'введите код подтверждения - '
                          f'{confirmation_code}.')
        send_mail(letter_header, letter_message, 'admin@YaMDB.ru', [email])
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def api_token(request):
    """Функция первичной самостоятельной регистрации пользователя
    принимает только POST-запросы по следующему шаблону:
    {
        "username": "string",
        "confirmation_code": "string"
    }
    Возвращает JWT-токен.
    """
    confirmation_code = request.data['confirmation_code']
    username = request.data['username']
    user = User.objects.get(username=username)
    if default_token_generator.check_token(user, confirmation_code):
        token = get_tokens_for_user(user)
        serializer = TokenSerializer(data=token)
        return Response(serializer.initial_data, status=status.HTTP_200_OK)
    return Response({'confirmation_code': ["Invalid token"]},
                    status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAdmin,)
    lookup_field = 'username'


    @action(['GET', 'PATCH'],
            url_path='me',
            detail=False,
            permission_classes=(IsAuthenticated,))
    def get_data_by_owner(self, request):
        """Метод переопределяет поведение UserViewSet
        в случае, когда url представлен '/users/me/.'
        """
        serializer = UserSerializer(request.user)
        if request.method == 'PATCH':
            if request.user.is_admin:
                serializer = UserSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
            else:
                serializer = UserSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data)
