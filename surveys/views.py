from curiositymachine.decorators import whitelist
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView, View
from json import JSONDecodeError
from urllib.parse import urlparse
from . import get_survey
from .updating import Updating
from .api import Surveymonkey
from .jobs import update_status
from .models import *
import django_rq
import json
import logging

logger = logging.getLogger(__name__)
api = Surveymonkey()

class SurveyResponseHook(View):

    def head(self, request, *args, **kwargs):
        return HttpResponse('OK') # needed to register as Surveymonkey webhook target

    def get(self, request, *args, **kwargs):
        if settings.ALLOW_SURVEY_RESPONSE_HOOK_BYPASS:
            sr = SurveyResponse.objects.get(id=request.GET["cmtoken"])
            Updating(sr, ResponseStatus.COMPLETED).run()
            return HttpResponseRedirect('/')
        else:
            raise Http404

    def post(self, request, *args, **kwargs):
        if api.valid(request.body, request.META['HTTP_SM_SIGNATURE'].encode("ascii")):
            try:
                data = json.loads(request.body)
                survey_id = data['filter_id']
                response_id = data['object_id']
                django_rq.enqueue(update_status, survey_id, response_id)
                logger.info("Update job queued for survey_id=%s response_id=%s", survey_id, response_id)
            except JSONDecodeError:
                logger.error("Error decoding webhook request body as JSON: %s" % request.body)
                raise
            except KeyError:
                logger.error("Key error when processing webhook data: %s" % data)
                raise
        else:
            logger.warning("Invalid POST to SurveyResponseHook")
            
        return HttpResponse('THX')
 
status_hook = csrf_exempt(SurveyResponseHook.as_view())

class SurveyCompletedView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        token_var = settings.SURVEYMONKEY_TOKEN_VAR
        token = self.request.GET.get(token_var, None)

        surveyresponse = get_object_or_404(SurveyResponse, id=token, user=self.request.user)

        Updating(surveyresponse, ResponseStatus.COMPLETED).run()
        if surveyresponse.message:
            messages.success(self.request, surveyresponse.message)

        view = getattr(surveyresponse, "redirect", "profiles:home")

        return reverse(view)

completed = whitelist('maybe_public')(login_required(SurveyCompletedView.as_view()))
