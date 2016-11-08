import operator

class Reversed:
    """
    Reverses the natural sort order of the value
    """

    def __init__(self, value):
        self.value = value

for x in ['__lt__', '__le__', '__eq__', '__ne__', '__ge__', '__gt__']:
    op = getattr(operator, x)
    setattr(Reversed, x, lambda self, other, op=op: op(other.value, self.value))

def latest_student_comment_sort(o):
    """
    Sorts progresses decorated with `latest_student_comment`, as in the `student_detail` view function.
    Sorts by most recent latest_student_comment creation date first, then breaks ties with challenge name.
    Objects without a latest_student_comment come *after* objects with.
    """
    if o.latest_student_comment:
        return (0, Reversed(o.latest_student_comment.created), o.challenge.name)
    else:
        return (1, o.challenge.name)    # this case is irrelevant if the page doesn't show uncommented progresses

class StudentSorter():
    def __init__(self, strategy=None):
        #TODO: make this take a query object or something? it turns query params into proper sorting
        self.strategy = strategy or 'first_name'

    def sort(self, qs):
        if self.strategy == 'first_name':
            return qs.extra(
                select={"has_first_name": "(first_name <> '') IS TRUE"},
                order_by=["-has_first_name", "first_name", "username"]
            )
        elif self.strategy == 'last_name':
            return qs.extra(
                select={"has_last_name": "(last_name <> '') IS TRUE"},
                order_by=["-has_last_name", "last_name", "username"]
            )
        elif self.strategy == 'username':
            return qs.order_by('username')
