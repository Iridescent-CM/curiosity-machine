import operator
from enum import Enum
from django.http import QueryDict

class Reversed:
    """
    Reverses the natural sort order of the value
    """

    def __init__(self, value):
        self.value = value

for x in ['__lt__', '__le__', '__eq__', '__ne__', '__ge__', '__gt__']:
    op = getattr(operator, x)
    setattr(Reversed, x, lambda self, other, op=op: op(other.value, self.value))

def latest_user_comment_sort(o):
    """
    Sorts progresses decorated with `latest_user_comment`, as in the `student_detail` view function.
    Sorts by most recent latest_user_comment creation date first, then breaks ties with challenge name.
    Objects without a latest_user_comment come *after* objects with.
    """
    if o.latest_user_comment:
        return (0, Reversed(o.latest_user_comment.created), o.challenge.name)
    else:
        return (1, o.challenge.name)    # this case is irrelevant if the page doesn't show uncommented progresses

class Sorter():
    """
    Base class for sorters that specify sort strategies, implement the algorithms, and manage
    some querystring processing and context data helpers.

    Subclasses should contain an inner subclass of the Strategy enum that contains strategy names and
    short names. A default strategy should be set as `default` on the class and the shortnames should
    be listed as `shortnames`. An implementation of `def sort(self, obj)` should also be provided that
    does sorting. Unhandled strategies can be sent up to `super()`.
    """

    class Strategy(Enum):
        @property
        def display_name(self):
            return self.name.capitalize().replace('_', ' ')

    def __init__(self, strategy=None, param="sort", query=None):
        self.param = param

        if strategy != None and not isinstance(strategy, self.Strategy):
            raise TypeError('strategy argument must be a %s.Strategy' % self.__class__)

        self.query = query
        if query != None and param in query:
            self.strategy = self.Strategy[query[param]]
        else:
            self.strategy = strategy or self.default

    def strategies(self):
        strats = []
        for short in self.shortnames:
            if self.query:
                qd = self.query.copy()
            else:
                qd = QueryDict(mutable=True)
            qd[self.param] = short
            strats.append({
                "name": self.Strategy[short].display_name,
                "url": "?%s" % qd.urlencode()
            })
        return strats

    def selected(self):
        return self.strategy.display_name

    def sort(self, *args):
        raise NotImplementedError('No sort strategy for %s' % self.strategy)

class StudentSorter(Sorter):

    class Strategy(Sorter.Strategy):
        first_name = 0
        f = 0
        last_name = 1
        l = 1
        username = 2
        u = 2

    default = Strategy.first_name
    shortnames = ['f', 'l', 'u']

    def sort(self, qs):
        """
        Expects a User queryset and adds sorting based on strategy.
        """
        if self.strategy == self.Strategy.first_name:
            return qs.extra(
                select={
                    "has_first_name": "(first_name <> '') IS TRUE",
                    "lower_first_name": "lower(first_name)",
                    "lower_username": "lower(username)",
                },
                order_by=["-has_first_name", "lower_first_name", "lower_username"]
            )
        elif self.strategy == self.Strategy.last_name:
            return qs.extra(
                select={
                    "has_last_name": "(last_name <> '') IS TRUE",
                    "lower_last_name": "lower(last_name)",
                    "lower_username": "lower(username)",
                },
                order_by=["-has_last_name", "lower_last_name", "lower_username"]
            )
        elif self.strategy == self.Strategy.username:
            return qs.extra(
                select={
                    "lower_username": "lower(username)",
                },
                order_by=["lower_username"]
            )
        else:
            return super().sort(qs)

class ProgressSorter(Sorter):

    class Strategy(Sorter.Strategy):
        most_recent_comment = 0
        m = 0
        challenge_name = 1
        c = 1

    default = Strategy.most_recent_comment
    shortnames = ['m', 'c']

    def sort(self, l):
        """
        Expects a list of Progresses decorated with `latest_user_comment` and sorts based on strategy.
        """
        if self.strategy == self.Strategy.most_recent_comment:
            return sorted(l, key=latest_user_comment_sort)
        elif self.strategy == self.Strategy.challenge_name:
            return sorted(l, key=lambda o: o.challenge.name.lower())
        else:
            return super().sort(qs)
