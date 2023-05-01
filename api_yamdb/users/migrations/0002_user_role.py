# Generated by Django 3.2 on 2023-04-26 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('USER', 'user'), ('MODERATOR', 'moderator'), ('ADMIN', 'admin')], default='user', max_length=10, verbose_name='Статус'),
        ),
    ]