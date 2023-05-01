from django.db.models import Avg
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from reviews.models import Category, Genre, Review, Title
from .serializers import (SignupSerializer, TokenSerializer,
                          UserSerializer, CommentSerializer, 
                          CategorySerializer, GenreSerializer,
                          ReviewSerializer, TitleBaseSerializer, 
                          TitlePostSerializer)
from .validators import is_username_not_me
from .permissions import IsAdmin, IsAdminOrReadOnly
from .filters import TitleFilter
from .mixins import ListCreateDeleteViewSet

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
