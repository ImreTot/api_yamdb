# Generated by Django 3.2 on 2023-05-02 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='confirmation_code',
            field=models.CharField(blank=True, default='none_code', max_length=255, verbose_name='код подтверждения'),
        ),
    ]
