import pytest
from django.forms.models import model_to_dict
from django.urls import reverse
from mentors.factories import *
from students.factories import *
from ..factories import *
from ..models import *

@pytest.mark.django_db
def test_endpoint_requires_login(client):
    assert client.post(
        reverse("educators:update_impact_survey"),
        model_to_dict(ImpactSurveyFactory())
    ).status_code == 403

@pytest.mark.django_db
def test_endpoint_requires_educator(client):
    MentorFactory(username='mentor', password='123123')
    client.login(username='mentor', password='123123')
    assert client.post(
        reverse("educators:update_impact_survey"),
        model_to_dict(ImpactSurveyFactory())
    ).status_code == 403

    StudentFactory(username='student', password='123123')
    client.login(username='student', password='123123')
    assert client.post(
        reverse("educators:update_impact_survey"),
        model_to_dict(ImpactSurveyFactory())
    ).status_code == 403

@pytest.mark.django_db
def test_endpoint_creates_model(client):
    user = EducatorFactory(username='user', password='123123')
    client.login(username='user', password='123123')

    assert ImpactSurvey.objects.filter(user=user).count() == 0

    client.post(
        reverse("educators:update_impact_survey"),
        model_to_dict(ImpactSurveyFactory(student_count=101))
    )
    client.post(
        reverse("educators:update_impact_survey"),
        model_to_dict(ImpactSurveyFactory(student_count=102))
    )

    assert ImpactSurvey.objects.filter(user=user).count() == 2

@pytest.mark.django_db
def test_endpoint_400s_for_bad_data(client):
    user = EducatorFactory(username='user', password='123123')
    client.login(username='user', password='123123')

    d = model_to_dict(ImpactSurveyFactory())
    d['student_count'] = "ten"
    assert client.post(reverse("educators:update_impact_survey"), d).status_code == 400
