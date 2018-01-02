import pytest
from django.core.exceptions import ValidationError
from ..allauth_adapter import AllAuthAdapter

@pytest.mark.django_db
def test_clean_username():
    adapter = AllAuthAdapter()
    assert adapter.clean_username("fine")
    with pytest.raises(ValidationError):
        adapter.clean_username("😱😱😱")