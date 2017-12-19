from allauth.account.models import EmailAddress
from django import forms
from django.core.exceptions import ValidationError

class ProfileModelForm(forms.ModelForm):

    email = forms.EmailField(label="E-mail", required=True) # TODO: limit length

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = kwargs.pop('user')
        if "initial" not in kwargs:
            kwargs["initial"] = {}
        initial = self.get_initial_from_user(self.user)
        initial.update(kwargs["initial"])
        kwargs["initial"] = initial
        super().__init__(*args, **kwargs)

    def get_role(self):
        raise NotImplementedError("Subclasses must implement this method to return the correct UserRole")

    def get_initial_from_user(self, user, **kwargs):
        emailobj = EmailAddress.objects.get_primary(user)
        initial = {
            'email': emailobj.email if emailobj else user.email if user.email else None
        }
        initial.update(kwargs)
        return initial

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
            self.user.full_clean(exclude=['username'])
        except ValidationError as e:
            self._update_errors(e)

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError(str(
                "save without commit not implemented "
                "due to multiple connected objects"
            ))

        # set the role first so we have it in signal handlers
        self.user.extra.role = self.get_role().value
        self.user.extra.save()

        obj = super().save(commit=False)

        obj = self.save_related(obj)
        self.user.save()

        obj.user = self.user
        obj.save()

        if "email" in self.changed_data:
            emailobj = EmailAddress.objects.add_email(
                self.request,
                self.user,
                self.cleaned_data["email"],
                confirm=True
            )
            emailobj.set_as_primary()

        return obj
