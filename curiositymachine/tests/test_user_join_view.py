import pytest
import mock
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect

User = get_user_model()

from profiles.models import Profile
from ..views.generic import UserJoinView

def test_redirects_logged_in_user(rf):
    request = rf.get('/whatever')
    user = User()
    profile = Profile(user=user)
    request.user = user
    view = UserJoinView.as_view(logged_in_redirect='/redirect')
    assert type(view(request)) == HttpResponseRedirect
    assert view(request).url == '/redirect'

def test_sets_source_in_initial_form_data(rf):
    request = rf.get('/whatever')
    request.user = AnonymousUser()

    m = mock.MagicMock()
    view = UserJoinView.as_view(form_class=m)
    view(request, source='source')

    args = m.call_args
    assert 'initial' in args[1]
    assert 'source' in args[1]['initial']
    assert args[1]['initial']['source'] == 'source'

def test_sets_source_in_form_data_from_url(rf):
    request = rf.post('/whatever', {'source': None})
    request.user = AnonymousUser()

    class SubUserJoinView(UserJoinView):
        def form_valid(self, form):
            pass

    m = mock.MagicMock()
    view = SubUserJoinView.as_view(form_class=m)
    view(request, source='source')

    args = m.call_args
    assert 'data' in args[1]
    assert 'source' in args[1]['data']
    assert args[1]['data']['source'] == 'source'

def test_strips_source_if_not_in_url(rf):
    request = rf.post('/whatever', {'source': 'source'})
    request.user = AnonymousUser()

    class SubUserJoinView(UserJoinView):
        def form_valid(self, form):
            pass

    m = mock.MagicMock()
    view = SubUserJoinView.as_view(form_class=m)
    view(request)

    args = m.call_args
    assert 'data' in args[1]
    assert 'source' not in args[1]['data']

def test_templates(rf):
    request = rf.get('/whatever')
    request.user = AnonymousUser()

    m = mock.MagicMock()
    view = UserJoinView.as_view(form_class=m, prefix='usertype')

    response = view(request)
    assert response.template_name == ['profiles/usertype/join.html']

    response = view(request, source='somesource')
    assert response.template_name == ['profiles/sources/somesource/usertype/join.html', 'profiles/usertype/join.html']

def test_redirects_to_success_url(rf):
    request = rf.post('/whatever', {})
    request.user = AnonymousUser()

    class SubUserJoinView(UserJoinView):
        def create_user(self, form):
            return mock.MagicMock()

    m = mock.MagicMock()
    view = SubUserJoinView.as_view(form_class=m, prefix='usertype', success_url='/success')

    response = view(request)
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == '/success'

def test_redirects_to_welcome_url_from_form(rf):
    request = rf.post('/join/thisone/', {'welcome': 'true'})
    request.user = AnonymousUser()

    class SubUserJoinView(UserJoinView):
        def create_user(self, form):
            return mock.MagicMock()

    m = mock.MagicMock()
    view = SubUserJoinView.as_view(form_class=m, success_url='/success')

    response = view(request, source='thisone')
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == '/welcome/thisone'

def test_puts_next_query_param_in_context(rf):
    request = rf.get('/whatever?next=/next/')
    request.user = AnonymousUser()

    m = mock.MagicMock()
    view = UserJoinView.as_view(form_class=m)
    response = view(request)

    assert "next" in response.context_data
    assert response.context_data["next"] == "/next/"

def test_redirects_to_next_param(rf):
    request = rf.post('/whatever/', {'next': '/next/'})
    request.user = AnonymousUser()

    class SubUserJoinView(UserJoinView):
        def create_user(self, form):
            return mock.MagicMock()

    m = mock.MagicMock()
    view = SubUserJoinView.as_view(form_class=m, success_url='/success')

    response = view(request)
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == '/next/'
