from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Review, Title
from api_yamdb.settings import ADMIN_EMAIL
from .filters import TitleFilter
from .mixins import ListCreateDeleteViewSet
from .permissions import (IsAdminOrReadOnly, IsAdminOrSuperuser,
                          IsAuthorOrModerPlusOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, SignupSerializer,
                          TitleBaseSerializer, TitlePostSerializer,
                          TokenSerializer, UserIsAdminSerializer,
                          UserSerializer)

User = get_user_model()


def create_confirmation_code_and_email(user):
    confirmation_code = default_token_generator.make_token(
        user
    )
    user.confirmation_code = confirmation_code
    user.save()
    letter_header = 'Подтверждение регистрации на сайте YaMDB'
    letter_message = (f'Здравствуйте!\n'
                      f'Вы зарегистрировались на сайте YaMDB, '
                      f'оставив username - {user.username} '
                      f'и email - {user.email}.\n'
                      f'Чтобы завершить регистрацию, '
                      f'введите код подтверждения - '
                      f'{user.confirmation_code}.')
    send_mail(letter_header,
              letter_message,
              ADMIN_EMAIL,
              [user.email])


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
    if User.objects.filter(username=request.data.get('username', []),
                           email=request.data.get('email', [])).exists():
        return Response(request.data, status.HTTP_200_OK)
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    create_confirmation_code_and_email(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


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
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.data
    confirmation_code = data.get('confirmation_code', [])
    username = data.get('username', [])
    user = get_object_or_404(User, username=username)
    if default_token_generator.check_token(user, confirmation_code):
        token = get_tokens_for_user(user)
        return Response(token, status=status.HTTP_200_OK)
    return Response({'confirmation_code': ['Invalid token']},
                    status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserIsAdminSerializer
    queryset = User.objects.all()
    permission_classes = (IsAdminOrSuperuser,)
    lookup_field = 'username'
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'head', 'options', 'patch', 'delete']

    @action(methods=['GET', 'PATCH'],
            url_path='me',
            detail=False,
            permission_classes=(IsAuthenticated,))
    def get_data_by_owner(self, request):
        """Метод переопределяет поведение UserViewSet
        в случае, когда url представлен '/users/me/.'
        """
        if request.method == 'PATCH':
            if request.user.is_admin or request.user.is_superuser:
                serializer = UserIsAdminSerializer(
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
        serializer = UserSerializer(request.user,
                                    data=request.data,
                                    partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class CategoryViewSet(ListCreateDeleteViewSet):
    queryset = Category.objects.get_queryset()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)


class GenreViewSet(ListCreateDeleteViewSet):
    queryset = Genre.objects.get_queryset()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
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
    permission_classes = (
        IsAuthorOrModerPlusOrReadOnly, IsAuthenticatedOrReadOnly
    )

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
    permission_classes = (
        IsAuthorOrModerPlusOrReadOnly, IsAuthenticatedOrReadOnly
    )

    def get_review(self):
        id = self.kwargs.get('review_id')
        return get_object_or_404(Review, id=id)

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
