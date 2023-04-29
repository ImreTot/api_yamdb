from django.db import models
from django.contrib.auth.models import AbstractUser

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'

CHOICES = (
    (USER, 'user'),
    (MODERATOR, 'moderator'),
    (ADMIN, 'admin'),
)


class User(AbstractUser):
    username = models.CharField(
        max_length=200,
        unique=True,
        blank=False,
        null=False
    )
    email = models.EmailField(
        unique=True,
        max_length=300,
        blank=False,
        null=False,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=200,
        blank=True,
        null=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=200,
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

    def __str__(self):
        return self.username
    