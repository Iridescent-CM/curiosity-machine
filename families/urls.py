from django.conf.urls import url
from rest_framework.routers import SimpleRouter
from .views import *

urlpatterns = [
    url(r'^profile/new/$', create, name="create_profile"),
    url(r'^profile/edit/$', edit, name="edit_profile"),
    url(r'^conversion/$', conversion, name="conversion"),
    url(r'^home/$', home, name="home"),
    url(r'^lessons/$', lessons, name="lessons"),
    url(r'^submission/$', submission, name="submission"),
    url(r'^awardforce/$', awardforce, name="awardforce"),
    url(r'^permission/new/$', sign_slip, name="create_permissionslip"),
]

router = SimpleRouter()
router.register(r'checklist', SubmissionChecklistViewSet, base_name="checklist")
urlpatterns += router.urls

if settings.DEBUG:
    urlpatterns += [
        url(r'^interruption/prereq/$', prereq_interruption),
        url(r'^interruption/postsurvey/$', postsurvey_interruption),
    ]