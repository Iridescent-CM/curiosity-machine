import pytest
from .models import Unit

@pytest.fixture
def unit():
    return Unit.objects.create(name='unit1')

@pytest.mark.django_db
def test_units(client, unit):
    response = client.get('/units/')
    assert response.status_code == 200
    assert len(response.context['units']) == 1


@pytest.mark.django_db
def test_unit(client, unit):
    response = client.get('/units/%s/' % str(unit.id))
    assert response.status_code == 200
    assert response.context['unit'].id == unit.id