from allauth.account.models import EmailAddress
from django import forms
from django.core.exceptions import ValidationError

class RelatedModelFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for relatedname, formclass in self.related_forms:
            for fieldname, field in formclass.base_fields.items():
                self.fields[fieldname] = field

    def get_initial(self, user, instance, **kwargs):
        related_initial = {}
        for relatedname, formclass in self.related_forms:
            form = formclass(instance=getattr(instance, relatedname, None))
            related_initial.update(form.initial)
        return super().get_initial(user, instance, **related_initial, **kwargs)

    def proxy_clean(self, cleaned_data, formclass):
        form = formclass(data=cleaned_data)
        form.full_clean()
        for fieldname, errors in form.errors.as_data().items():
            if fieldname == '__all__':
                fieldname = None
            for error in errors:
                if not self.has_error(fieldname, code=error.code):
                    self.add_error(fieldname, error)
        cleaned_data.update(form.cleaned_data)
        return cleaned_data

    def clean(self):
        cleaned_data = super().clean()
        for name, formclass in self.related_forms:
            cleaned_data = self.proxy_clean(cleaned_data, formclass)
        return cleaned_data

    def save_related(self, obj):
        for relatedname, formclass in self.related_forms:
            form = formclass(self.cleaned_data, instance=getattr(obj, relatedname, None))
            if form.is_valid():
                related = form.save()
                setattr(obj, relatedname, related)
            else:
                raise ValueError("Could not save because related form for %s did not validate" % relatedname)

        return obj

class ProfileModelForm(forms.ModelForm):

    email = forms.EmailField(label="E-mail", required=True) # TODO: limit length

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = kwargs.pop('user')
        if "initial" not in kwargs:
            kwargs["initial"] = {}
        initial = self.get_initial(self.user, kwargs.get('instance', None))
        initial.update(kwargs["initial"])
        kwargs["initial"] = initial
        super().__init__(*args, **kwargs)

    def get_role(self):
        raise NotImplementedError("Subclasses must implement this method to return the correct UserRole")

    def get_initial(self, user, instance, **kwargs):
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
