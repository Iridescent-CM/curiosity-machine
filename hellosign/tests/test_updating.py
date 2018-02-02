import pytest
import mock
from ..factories import *
from ..models import *
from ..updating import Updating

@pytest.mark.django_db
def test_updates_status():
    signature = SignatureFactory()
    new_status = SignatureStatus.SIGNED
    assert signature.status != new_status
    Updating(signature, new_status).run()
    assert signature.status == new_status

@pytest.mark.django_db
def test_gives_signer_a_chance_to_act():
    signature = SignatureFactory()
    new_status = SignatureStatus.SIGNED
    signer = mock.MagicMock()
    Updating(signature, new_status, signer=signer).run()
    assert signer.on.called

@pytest.mark.django_db
def test_short_circuits_same_status():
    signature = SignatureFactory(status=SignatureStatus.SIGNED)
    new_status = SignatureStatus.SIGNED
    signer = mock.MagicMock()
    Updating(signature, new_status, signer=signer).run()
    assert not signer.on.called
