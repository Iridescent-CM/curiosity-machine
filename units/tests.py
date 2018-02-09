import pytest
from django.contrib.auth import get_user_model
from educators.factories import *
from profiles.factories import *
from profiles.models import UserRole
from .factories import *
from .models import Unit

User = get_user_model()

@pytest.fixture
def unit():
    return UnitFactory(name='unit1', listed=True)

@pytest.fixture
def educator():
    return EducatorFactory(username="educator", password='secret')

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