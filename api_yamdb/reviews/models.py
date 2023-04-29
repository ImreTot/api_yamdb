'''
При удалении объекта пользователя User должны удаляться все отзывы и комментарии этого пользователя (вместе с оценками-рейтингами).
При удалении объекта произведения Title должны удаляться все отзывы к этому произведению и комментарии к ним.
При удалении объекта отзыва Review должны быть удалены все комментарии к этому отзыву.
При удалении объекта категории Category не нужно **удалять связанные с этой категорией произведения.
При удалении объекта жанра Genre не нужно удалять связанные с этим жанром произведения.
'''

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .validators import year_validator


User = get_user_model() # заменить модель юзера

class PubDateNowModel(models.Model):
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ['-pub_date']
        abstract = True

class Category(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Категория',
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Адрес',
    )

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Жанр',
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Адрес',
    )

    class Meta:
        verbose_name = 'genre'
        verbose_name_plural = 'genres'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название',
    )
    year = models.PositiveBigIntegerField(
        validators= (year_validator,),
        verbose_name='Дата выхода',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание',
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанр',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория',
        null=True,
    )

    class Meta:
        ordering = ('year',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


# ============================================================================


class Review(PubDateNowModel):
    """Модель отзыва."""
    
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    text = models.TextField('Отзыв')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор отзыва',
        related_name='review_author'
    )
    score = models.PositiveSmallIntegerField(
        'Рейтинг произведения',
        validators=[
            MinValueValidator(
                settings.MIN_SCORE,
                message=f'Минимальная оценка - {settings.MIN_SCORE}',
            ),
            MaxValueValidator(
                settings.MAX_SCORE,
                message=f'Максимальная оценка - {settings.MAX_SCORE}',
            ),
        ],
    )

    class Meta:
        models.UniqueConstraint(
            fields=('title', 'author'),
            name='unique_review'
        )
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        nl = '\n'
        return f'Отзыв: {self.text}{nl}Оценка: {self.score}'


class Comment(PubDateNowModel):
    """Модель комментария."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='отзыв',
        related_name='comments',
    )
    text = models.TextField('Комментарий')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
        related_name='comment_author'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
