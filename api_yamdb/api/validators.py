from rest_framework import serializers


def is_username_not_me(username):
    """Функция проверяет, что переданный аргумент - не 'me'
    вне зависимости от регистра."""
    if username.lower() == 'me':
        raise serializers.ValidationError({
            'username': 'username can\'t be \'me\'.'
        })
    return username
