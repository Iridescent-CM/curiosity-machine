import mock
import pytest
from curiositymachine import signals
from django.contrib.auth import get_user_model
from students.factories import *
from ..factories import *


@pytest.mark.django_db
def test_signal_created_account():
    handler = mock.MagicMock()
    signal = signals.created_account
    signal.connect(handler)

    user = get_user_model().objects.create(username='user', email='email')
    handler.assert_called_once_with(signal=signal, sender=user)

@pytest.mark.django_db
def test_signal_created_profile():
    handler = mock.MagicMock()
    signal = signals.created_profile
    signal.connect(handler)

    user = UserFactory()
    profile = StudentProfileFactory(user=user)
    handler.assert_called_once_with(signal=signal, sender=user)

