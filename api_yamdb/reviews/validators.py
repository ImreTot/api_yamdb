from django.utils import timezone
from rest_framework.exceptions import ValidationError


def year_validator(value):
    if value < 0 or value > timezone.now().year:
        raise ValidationError(f'Год {value} указан неправильно.')
