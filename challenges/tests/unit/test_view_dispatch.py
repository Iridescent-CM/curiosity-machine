import pytest
from challenges.views import ViewDispatch
from django.contrib.auth.models import AnonymousUser

pytestmark = pytest.mark.unit

def test_view_dispatch_requires_subclass():
    with pytest.raises(NotImplementedError):
        ViewDispatch.select_view_class(AnonymousUser())
