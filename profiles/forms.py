from django import forms
from django.core.exceptions import ValidationError

class ProfileModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def get_role(self):
        raise NotImplementedError("Subclasses must implement this method to return the correct UserRole")

    def save_related(self, obj):
        return obj

    def update_user(self):
        pass

    def full_clean(self):
        super().full_clean()
        if not self.is_bound:
            return

        self.update_user()
        try:
            self.user.full_clean()
        except ValidationError as e:
            self._update_errors(e)

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError(str(
                "save without commit not implemented "
                "due to multiple connected objects"
            ))

        obj = super().save(commit=False)

        obj = self.save_related(obj)
        self.user.save()

        obj.user = self.user
        obj.save()

        self.user.extra.role = self.get_role().value
        self.user.extra.save()

        return obj
