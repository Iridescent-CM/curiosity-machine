import pytest
import mock
from django.contrib.auth.models import User
#from django.core.urlresolvers import reverse
from django.utils.timezone import now
from .mailer import deliver_email
from datetime import date, timedelta

@pytest.fixture
def student():
    student = User.objects.create_user(username='student', email='student@example.com', password='password')
    student.profile.approved = True
    student.profile.is_student = True
    student.profile.birthday = now() - timedelta(days=(365 * 16))
    student.profile.save()
    return student


@pytest.mark.django_db
def test_override_subject(student):
	assert deliver_email('welcome', student.profile) == None
	assert deliver_email('welcome', student.profile, subject='test') == None