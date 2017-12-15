import pytest
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now
from images.factories import *
from ..factories import *
from ..views import ListView

@pytest.mark.django_db
def test_mentor_community_orders_by_image_then_date():
    mentor1 = MentorFactory(username="mentor1", date_joined=now()-relativedelta(days=0))
    mentor2 = MentorFactory(username="mentor2", date_joined=now()-relativedelta(days=1))
    mentor3 = MentorFactory(
        username="mentor3",
        date_joined=now()-relativedelta(days=2),
        mentorprofile__image=ImageFactory()
    )
    mentor4 = MentorFactory(
        username="mentor4",
        date_joined=now()-relativedelta(days=3),
        mentorprofile__image=ImageFactory()
    )
    view = ListView()
    page_order = list(view.get_queryset().all().values_list('user__username', flat=True))
    assert page_order == ['mentor3', 'mentor4', 'mentor1', 'mentor2']