from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from educators.factories import *
from families.factories import *
from mentors.factories import *
from parents.factories import *
from students.factories import *
from ..admin import UserAdminWithExtra
import mock
import pytest

@pytest.fixture
def admin():
    site = AdminSite()
    return UserAdminWithExtra(get_user_model(), site)

@pytest.fixture
def req():
    return mock.MagicMock()

@pytest.mark.parametrize("factoryclass,relatedname", [
    (StudentFactory, 'studentprofile'),
    (EducatorFactory, 'educatorprofile'),
    (MentorFactory, 'mentorprofile'),
    (ParentFactory, 'parentprofile')
])
@pytest.mark.django_db
def test_search_on_old_city_field(factoryclass, relatedname, admin, req):
    fieldname = relatedname + "__city"
    user = factoryclass(**{fieldname: "Springfield"})
    qs, distinct = admin.get_search_results(req, admin.get_queryset(req), "springfield")
    assert user in qs.all()

@pytest.mark.parametrize("factoryclass,relatedname", [
    (EducatorFactory, 'educatorprofile'),
    (FamilyFactory, 'familyprofile')
])
@pytest.mark.django_db
def test_search_on_location_city_field(factoryclass, relatedname, admin, req):
    fieldname = relatedname + "__location__city"
    user = factoryclass(**{fieldname: "Springfield"})
    qs, distinct = admin.get_search_results(req, admin.get_queryset(req), "springfield")
    assert user in qs.all()

@pytest.mark.parametrize("factoryclass,relatedname", [
    (EducatorFactory, 'educatorprofile'),
    (FamilyFactory, 'familyprofile')
])
@pytest.mark.django_db
def test_lookup_search_on_location_state_field(factoryclass, relatedname, admin, req):
    fieldname = relatedname + "__location__state"
    user = factoryclass(**{fieldname: "US-HI"})
    assert user in admin.get_search_results(req, admin.get_queryset(req), "hawaii")[0].all()

@pytest.mark.parametrize("factoryclass,relatedname", [
    (EducatorFactory, 'educatorprofile'),
    (FamilyFactory, 'familyprofile')
])
@pytest.mark.django_db
def test_multiword_lookup_search_on_location_state_field(factoryclass, relatedname, admin, req):
    fieldname = relatedname + "__location__state"
    user = factoryclass(**{fieldname: "US-RI"})
    assert user in admin.get_search_results(req, admin.get_queryset(req), "rhode island")[0].all()

@pytest.mark.parametrize("factoryclass,relatedname", [
    (EducatorFactory, 'educatorprofile'),
    (FamilyFactory, 'familyprofile')
])
@pytest.mark.django_db
def test_lookup_search_on_location_country_field(factoryclass, relatedname, admin, req):
    fieldname = relatedname + "__location__country"
    user = factoryclass(**{fieldname: "CA"})
    assert user in admin.get_search_results(req, admin.get_queryset(req), "canada")[0].all()

@pytest.mark.parametrize("factoryclass,relatedname", [
    (EducatorFactory, 'educatorprofile'),
    (FamilyFactory, 'familyprofile')
])
@pytest.mark.django_db
def test_multiword_lookup_search_on_location_country_field(factoryclass, relatedname, admin, req):
    fieldname = relatedname + "__location__country"
    user = factoryclass(**{fieldname: "NZ"})
    assert user in admin.get_search_results(req, admin.get_queryset(req), "new zealand")[0].all()
