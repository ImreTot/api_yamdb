from django.db import models
from django.contrib.auth.models import AbstractUser

CHOICES = (
    ('USER', 'user'),
    ('MODERATOR', 'moderator'),
    ('ADMIN', 'admin'),
)


class User(AbstractUser):
    role = models.CharField(
        verbose_name='Статус',
        max_length=10,
        default='user',
        choices=CHOICES,
        blank=False,
    )
    bio = models.TextField(
        verbose_name='Биография',
        blank=True
    )
