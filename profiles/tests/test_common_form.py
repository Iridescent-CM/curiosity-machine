import pytest

from ..forms.common import UserAndProfileForm


@pytest.mark.django_db
def test_case_insensitive_username_duplicates_dont_validate():

    class DerivedForm(UserAndProfileForm):
        class Meta(UserAndProfileForm.Meta):
            fields = ['username']

    form1 = DerivedForm({
        "username": "user"     
    })
    form1.save()

    form2 = DerivedForm({
        "username": "User"     
    })
    assert not form2.is_valid()
    assert form2.errors.as_data()["username"][0].code == 'duplicate'

