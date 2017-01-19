import pytest

from ..helpers.selectors import SelectorOption, GroupSelector

from memberships.factories import *
from profiles.factories import *

from django.http import QueryDict, Http404

def test_holds_extra_named_args():
    s = SelectorOption(query_param='x', query_value=1, text='hi', extra='something')
    assert s.query_param == 'x'
    assert s.query_value == 1
    assert s.text == 'hi'
    assert s.extra == 'something'

def test_equality_based_on_arg_values():
    assert SelectorOption(query_param='x', query_value=1, text='hi') == SelectorOption(query_param='x', query_value=1, text='hi')

    assert SelectorOption(query_param='x', query_value=1, text='hi') != SelectorOption(query_param='y', query_value=1, text='hi')
    assert SelectorOption(query_param='x', query_value=1, text='hi') != SelectorOption(query_param='x', query_value=2, text='hi')
    assert SelectorOption(query_param='x', query_value=1, text='hi') != SelectorOption(query_param='x', query_value=1, text='bye')

def test_updates_query_string():
    assert SelectorOption(query_param='x', query_value='1', text='hi', query=QueryDict()).GET == QueryDict('x=1')
    assert SelectorOption(query_param='x', query_value='1', text='hi', query=QueryDict('x=5')).GET == QueryDict('x=1')
    assert SelectorOption(query_param='x', query_value='1', text='hi', query=QueryDict('a=5')).GET == QueryDict('a=5&x=1')

@pytest.mark.django_db
def test_default_selector_option_template_attrs():
    membership = MembershipFactory()

    gs = GroupSelector(membership, query_param='x')
    assert len(gs.options) == 2

    assert gs.options[0].text == "All Students"
    assert gs.options[0].query_param == "x"
    assert gs.options[0].query_value == "all"
    assert gs.options[0].GET == QueryDict('x=all')

    assert gs.options[1].text == "Ungrouped"
    assert gs.options[1].query_param == "x"
    assert gs.options[1].query_value == "none"
    assert gs.options[1].GET == QueryDict('x=none')

@pytest.mark.django_db
def test_all_students_queryset_gets_all_students():
    students = StudentFactory.create_batch(10)
    educators = EducatorFactory.create_batch(2)
    membership = MembershipFactory(members=students + educators)

    gs = GroupSelector(membership)
    assert set(gs.options[0].queryset.all()) == set(students)

@pytest.mark.django_db
def test_ungrouped_queryset_gets_ungrouped_students():
    students = StudentFactory.create_batch(10)
    educators = EducatorFactory.create_batch(2)
    membership = MembershipFactory(members=students + educators)

    gs = GroupSelector(membership)
    assert set(gs.options[1].queryset.all()) == set(students)

    group = GroupFactory(membership=membership, members=students[0:5])
    gs = GroupSelector(membership)
    assert set(gs.options[2].queryset.all()) == set(students[5:])

@pytest.mark.django_db
def test_group_selector_option_template_attrs():
    membership = MembershipFactory()
    group = GroupFactory(name='group name', membership=membership)

    gs = GroupSelector(membership, query_param='x')
    assert len(gs.options) == 3

    assert gs.options[1].text == "group name"
    assert gs.options[1].query_param == "x"
    assert gs.options[1].query_value == group.id
    assert gs.options[1].GET == QueryDict('x=%d' % group.id)

@pytest.mark.django_db
def test_group_selector_option_ordering():
    membership = MembershipFactory()
    GroupFactory(name='b', membership=membership)
    GroupFactory(name='a', membership=membership)
    GroupFactory(name='c', membership=membership)

    gs = GroupSelector(membership)
    assert len(gs.options) == 5
    assert gs.options[1].text == "a"
    assert gs.options[2].text == "b"
    assert gs.options[3].text == "c"

@pytest.mark.django_db
def test_group_queryset_gets_group_students():
    students = StudentFactory.create_batch(10)
    educators = EducatorFactory.create_batch(2)
    membership = MembershipFactory(members=students + educators)
    group1 = GroupFactory(name="a", membership=membership, members=students[0:5])
    group2 = GroupFactory(name="b", membership=membership, members=students[5:])

    gs = GroupSelector(membership)
    assert gs.options[1].text == 'a'
    assert set(gs.options[1].queryset.all()) == set(students[0:5])
    assert gs.options[2].text == 'b'
    assert set(gs.options[2].queryset.all()) == set(students[5:])

@pytest.mark.django_db
def test_passes_query_params_through():
    membership = MembershipFactory()
    gs = GroupSelector(membership, query=QueryDict('a=1&b=2'), query_param='x')
    assert gs.options[0].GET == QueryDict('a=1&b=2&x=all')

@pytest.mark.django_db
def test_selects_from_query_params():
    membership = MembershipFactory()
    group = GroupFactory(membership=membership)
    assert GroupSelector(membership, query={}).selected.text == 'All Students'
    assert GroupSelector(membership, query={'g': 'all'}).selected.text == 'All Students'
    assert GroupSelector(membership, query={'g': 'none'}).selected.text == 'Ungrouped'
    assert GroupSelector(membership, query={'g': str(group.id)}).selected.text == group.name

@pytest.mark.django_db
def test_bad_selection_404s():
    membership = MembershipFactory()
    with pytest.raises(Http404):
        GroupSelector(membership, query={'g': '1'}).selected
