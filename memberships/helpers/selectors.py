from ..models import UserRole
from collections import OrderedDict
from django.http import QueryDict, Http404

class SelectorOption():
    def __init__(self, query_param=None, query_value=None, query=QueryDict(), text=None, **kwargs):
        self.query_param = query_param
        self.query_value = query_value
        self.text = text
        for k, v in kwargs.items():
            setattr(self, k, v)

        self.GET = self._update(query)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def _update(self, query):
        q = query.copy()
        q[self.query_param] = str(self.query_value)
        return q

class GroupSelector():
    query_param = 'g'

    def __init__(self, membership, query_param=None, query=None):
        if query_param is not None:
            self.query_param = query_param

        self.membership = membership
        if query is not None:
            self.query = query
        else:
            self.query = QueryDict()

        student_qs = self.membership.members.filter(profile__role=UserRole.student.value)

        self._map = OrderedDict()
        self._map['all'] = SelectorOption(
            text = "All Students",
            query_param = self.query_param,
            query_value = 'all',
            queryset = student_qs,
            query = self.query
        )

        for group in self.membership.group_set.order_by('name').all():
            self._map[str(group.id)] = SelectorOption(
                text=group.name,
                query_param=self.query_param,
                query_value=group.id,
                queryset = student_qs
                    .filter(member__groupmember__group=group),
                query = self.query
            )

        self._map['none'] = SelectorOption(
            text="Ungrouped",
            query_param=self.query_param,
            query_value='none',
            queryset = student_qs
                .exclude(member__groupmember__group__membership=self.membership),
            query = self.query
        )

    @property
    def options(self):
        return list(self._map.values())

    @property
    def selected(self):
        if not self.query:
            key = 'all'
        else:
            key = self.query.get(self.query_param, 'all')

        try:
            return self._map[key]
        except:
            raise Http404()
