from ..models import UserRole
from collections import OrderedDict

class SelectorOption():
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class GroupSelector():
    query_param = 'g'

    def __init__(self, membership, query_param=None, query=None):
        if query_param is not None:
            self.query_param = query_param

        self.membership = membership
        self.query = query

        student_qs = self.membership.members.filter(profile__role=UserRole.student.value)

        self._map = OrderedDict()
        self._map['all'] = SelectorOption(
            text = "All Students",
            query_param = self.query_param,
            query_value = 'all',
            queryset = student_qs
        )

        for group in self.membership.group_set.order_by('name').all():
            self._map[str(group.id)] = SelectorOption(
                text=group.name,
                query_param=self.query_param,
                query_value=group.id,
                queryset = student_qs
                    .filter(member__groupmember__group=group)
            )

        self._map['none'] = SelectorOption(
            text="Ungrouped",
            query_param=self.query_param,
            query_value='none',
            queryset = student_qs
                .exclude(member__groupmember__group__membership=self.membership)
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
        return self._map[key]
