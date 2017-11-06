from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

class UsernameUniquenessValidator:
    def __call__(self, value):
        if get_user_model().objects.filter(username__iexact=value).exists():
            raise ValidationError('A user with that username already exists.', code='duplicate')

    def __eq__(self, other):
        return isinstance(other, self.__class__)

username_validators = [UsernameUniquenessValidator(),]
