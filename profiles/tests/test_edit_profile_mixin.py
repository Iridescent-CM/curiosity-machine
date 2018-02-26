from curiositymachine.context_processors.google_analytics import get_events
from django.views.generic import *
from ..factories import *
from ..forms import *
from ..views import *
import mock
import pytest

def test_adds_event_on_create(rf):
    TestForm = mock.Mock()
    TestForm().get_role().name = 'role name'

    class TestCreateView(EditProfileMixin, CreateView):
        form_class = TestForm

    view = TestCreateView.as_view()

    req = rf.post('/whatever', {})
    req.user = UserFactory.build()
    req.session = {}

    view(req)

    evts = get_events(req)
    assert len(evts) == 1
    assert evts[0] == {"category": "profile", "action": "create", "label": "role name"}

def test_no_event_on_update(rf):
    TestForm = mock.Mock()
    TestForm().get_role().name = 'role name'

    class TestEditView(EditProfileMixin, UpdateView):
        form_class = TestForm
        queryset = mock.MagicMock()

    view = TestEditView.as_view()

    req = rf.post('/whatever', {})
    req.user = UserFactory.build()
    req.session = {}

    view(req, pk=1)

    evts = get_events(req)
    assert len(evts) == 0

