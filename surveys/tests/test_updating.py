import pytest
import mock
from ..factories import *
from ..models import *
from ..updating import Updating

@pytest.mark.django_db
def test_status_updated():
    sr = SurveyResponseFactory()
    new_status = ResponseStatus.COMPLETED
    assert sr.status != new_status
    Updating(sr, new_status).run()
    assert sr.status == new_status

@pytest.mark.django_db
def test_responder_has_chance_to_act():
    sr = SurveyResponseFactory()
    new_status = ResponseStatus.COMPLETED
    responder = mock.MagicMock()
    Updating(sr, new_status, responder=responder).run()
    assert responder.on.called
    
