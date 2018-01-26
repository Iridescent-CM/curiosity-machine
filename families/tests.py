import pytest
from images.factories import *
from students.factories import *
from .factories import *
from .forms import *

@pytest.mark.django_db
def test_converting_profiles_copies_image():
    image = ImageFactory()
    student = StudentFactory(studentprofile__image=image)
    studentprofile = student.studentprofile

    familyprofile = FamilyProfileFactory.build()
    form = FamilyProfileForm(
        user=student,
        data=FamilyProfileForm(user=student, instance=familyprofile).initial
    )
    assert form.is_valid()
    familyprofile = form.save()    
    assert familyprofile.user.extra.is_family
    assert familyprofile.image == studentprofile.image

@pytest.mark.django_db
def test_valid_form():
    user = FamilyFactory()
    data = dict(
        FamilyProfileForm(user=user, instance=user.familyprofile).initial,
    )
    f = FamilyProfileForm(user=user, data=data)
    assert f.is_valid()

@pytest.mark.django_db
def test_requires_city():
    user = FamilyFactory()
    data = dict(
        FamilyProfileForm(user=user, instance=user.familyprofile).initial,
        city=None
    )
    f = FamilyProfileForm(user=user, data=data)
    assert not f.is_valid()
    assert "city" in f.errors

@pytest.mark.django_db
def test_requires_country():
    user = FamilyFactory()
    data = dict(
        FamilyProfileForm(user=user, instance=user.familyprofile).initial,
        country=None
    )
    f = FamilyProfileForm(user=user, data=data)
    assert not f.is_valid()
    assert "country" in f.errors

@pytest.mark.django_db
def test_requires_state_if_US():
    user = FamilyFactory()
    data = dict(
        FamilyProfileForm(user=user, instance=user.familyprofile).initial,
        state=None
    )
    f = FamilyProfileForm(user=user, data=data)
    assert not f.is_valid()
    assert "state" in f.errors

    data = dict(
        FamilyProfileForm(user=user, instance=user.familyprofile).initial,
        state=None,
        country='CA'
    )
    f = FamilyProfileForm(user=user, data=data)
    assert f.is_valid()

@pytest.mark.django_db
def test_state_nulled_if_not_US():
    user = FamilyFactory()
    data = dict(
        FamilyProfileForm(user=user, instance=user.familyprofile).initial,
        state='US-AK',
        country='CA'
    )
    f = FamilyProfileForm(user=user, data=data)
    print(f.errors.as_json())
    assert f.is_valid()
    assert f.cleaned_data["country"] == "CA"
    assert f.cleaned_data["state"] == None
