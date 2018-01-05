from curiositymachine.forms import MediaURLField
from curiositymachine.widgets import FilePickerPickWidget
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget
from profiles.forms import ProfileModelForm
from profiles.models import UserRole
from .models import *

class FamilyProfileForm(ProfileModelForm):
    class Meta:
        model = FamilyProfile
        fields = ['phone']

    image_url = MediaURLField(
        label="Photo",
        mimetypes="image/*",
        widget=FilePickerPickWidget(attrs={
            "data-fp-opento": "WEBCAM",
            "data-fp-services": "WEBCAM,COMPUTER,CONVERT",
            "data-fp-conversions": "crop,rotate",
            "data-fp-cropratio": 1,
            "data-fp-cropforce": "force",
        }),
        required=False
    )

    phone = PhoneNumberField(widget=PhoneNumberInternationalFallbackWidget)

    def save_related(self, obj):
        if self.cleaned_data.get("image_url"):
            img = Image(source_url=self.cleaned_data['image_url']['url'])
            img.save()
            obj.image = img
        return obj

    def get_role(self):
        return UserRole.family
