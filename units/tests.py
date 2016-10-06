import pytest
from django.contrib.auth import get_user_model
from profiles.models import Profile
from .models import Unit

User = get_user_model()

@pytest.fixture
def unit():
    return Unit.objects.create(name='unit1', draft=False)

@pytest.fixture
def educator():
    educator = User(username="educator")
    educator.set_password('secret')
    educator_profile = Profile(is_educator=True)
    educator_profile.user = educator
    educator.save()
    educator_profile.user = educator
    educator_profile.save()
    return educator

@pytest.mark.django_db
def test_units_accessible_by_educator(client, unit, educator):
    client.login(username='educator', password='secret')
    response = client.get('/units/')
    assert response.status_code == 200
    assert len(response.context['units']) == 1


@pytest.mark.django_db
def test_unit_accessible_by_educator(client, unit, educator):
    client.login(username='educator', password='secret')
    response = client.get('/units/%s/' % str(unit.id))
    assert response.status_code == 200
    assert response.context['unit'].id == unit.id

@pytest.mark.django_db
def test_unit_accessible_by_id_or_slug(client, unit, educator):
    unit.slug="slug"
    unit.save(update_fields=["slug"])

    client.login(username='educator', password='secret')
    response = client.get('/units/%s/' % str(unit.id))
    assert response.status_code == 200
    response = client.get('/units/%s/' % str(unit.slug))
    assert response.status_code == 200