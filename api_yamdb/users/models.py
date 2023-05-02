import re
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.contrib.auth.tokens import default_token_generator
from django.db.models.signals import post_save
from django.core.validators import RegexValidator

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
USERNAME_REGEX = r'^[\w.@+-]+$'

CHOICES = (
    (USER, 'user'),
    (MODERATOR, 'moderator'),
    (ADMIN, 'admin'),
)


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        validators=[RegexValidator(
            regex=USERNAME_REGEX,
            message='Username should only contain letters, digits, and @/./+/-/_ characters.',
            code='invalid_username'
        )]
    )
    email = models.EmailField(
        unique=True,
        max_length=254,
        blank=False,
        null=False,
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
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_user(self):
        return self.role == USER


@receiver(post_save, sender=User)
def post_save(sender, instance, created, **kwargs):
    if created:
        confirmation_code = default_token_generator.make_token(
            instance
        )
        instance.confirmation_code = confirmation_code
        instance.save()
    