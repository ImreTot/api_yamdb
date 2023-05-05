from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    USERNAME_REGEX = r'^[\w.@+-]+$'
    CHOICES = (
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        validators=[RegexValidator(
            regex=USERNAME_REGEX,
            message='Username should only contain letters, '
                    'digits, and @/./+/-/_ characters.',
            code='invalid_username'
        )]
    )
    email = models.EmailField(
        unique=True,
        max_length=254,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=True,
        null=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=True,
        null=True
    )
    role = models.CharField(
        verbose_name='cтатус',
        max_length=10,
        default=USER,
        choices=CHOICES,
        blank=False,
    )
    bio = models.TextField(
        verbose_name='Биография',
        blank=True
    )
    confirmation_code = models.CharField(
        verbose_name='код подтверждения',
        max_length=255,
        default='none_code',
        null=False,
        blank=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_user(self):
        return self.role == self.USER
