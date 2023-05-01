from csv import DictReader

from django.core.management import BaseCommand

from reviews.models import (
    Title, Genre, Category, 
    TitleGenre, Review, Comment
)
from users.models import User


class Command(BaseCommand):
    """Загружает csv-файла в БД из папки static/data/."""

    def handle(self, *args, **options):
        for row in DictReader(open('static/data/category.csv',
                                   encoding="utf8")):
            category = Category(name=row['name'], id=row['id'],
                                slug=row['slug'])
            category.save()
        for row in DictReader(open('static/data/genre.csv', encoding="utf8")):
            genre = Genre(name=row['name'], id=row['id'], slug=row['slug'])
            genre.save()
        for row in DictReader(open('static/data/titles.csv', encoding="utf8")):
            title = Title(
                name=row['name'],
                id=row['id'],
                year=row['year'],
                category=Category.objects.get(pk=row['category'])
            )
            title.save()
        for row in DictReader(open('static/data/genre_title.csv',
                                   encoding="utf8")):
            genre_title = TitleGenre(
                id=row['id'],
                title=Title.objects.get(pk=row['title_id']),
                genre=Genre.objects.get(pk=row['genre_id'])
            )
            genre_title.save()
        for row in DictReader(open('static/data/users.csv', encoding="utf8")):
            user = User(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                role=row['role'],
                bio=row['bio'],
                first_name=row['first_name'],
                last_name=row['last_name']
            )
            user.save()
        for row in DictReader(open('static/data/titles.csv', encoding="utf8")):
            title = Title(
                name=row['name'],
                id=row['id'],
                year=row['year'],
                category=Category.objects.get(pk=row['category'])
            )
            title.save()
        for row in DictReader(open('static/data/review.csv',
                                   encoding="utf8")):
            review = Review(
                id=row['id'],
                title=Title.objects.get(pk=row['title_id']),
                text=row['text'],
                author=User.objects.get(pk=row['author']),
                score=row['score'],
                pub_date=row['pub_date']
            )
            review.save()
        for row in DictReader(open('static/data/comments.csv',
                                   encoding="utf8")):
            comment = Comment(
                id=row['id'],
                review=Review.objects.get(pk=row['review_id']),
                text=row['text'],
                author=User.objects.get(pk=row['author']),
                pub_date=row['pub_date']
            )
            comment.save()
