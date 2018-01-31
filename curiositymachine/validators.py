from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import re

class UsernameUniquenessValidator:
    def __call__(self, value):
        if get_user_model().objects.filter(username__iexact=value).exists():
            raise ValidationError('A user with that username already exists.', code='duplicate')

    def __eq__(self, other):
        return isinstance(other, self.__class__)

username_validators = [
    UsernameUniquenessValidator(),
    get_user_model().username_validator,
]

lower_slug_re = re.compile(r'^[-a-z0-9_]+\Z')
validate_lowercase_slug = RegexValidator(
    lower_slug_re,
    "Enter a valid 'slug' consisting of lowercase letters, numbers, underscores or hyphens.",
    'invalid'
)
