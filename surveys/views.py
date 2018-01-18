from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from json import JSONDecodeError
from .api import Surveymonkey
from .models import *
import base64
import django_rq
import hashlib
import hmac
import json
import logging
import requests

logger = logging.getLogger(__name__)
api = Surveymonkey()

def update_status(survey_id, response_id):
    token_var = settings.SURVEYMONKEY_TOKEN_VAR

    res = api.get("surveys/%s/responses/%s" % (survey_id, response_id))
    res.raise_for_status()

    data = res.json()
    try:
        custom_vars = data['custom_variables']
        new_status = data['response_status']
    except KeyError:
        logger.error("API response did not contain expected fields: %s" % data)
        raise

    token = custom_vars.get(token_var, None)
    if token:
        sr = SurveyResponse.objects.filter(id=token).first()
        if sr:
            status = ResponseStatus[new_status.upper()]
            sr.status = status
            sr.save(update_fields=['status'])
        else:
            logger.info("SurveyResponse not found for id=%s; assuming it's in another environment" % token)
    else:
        logger.info(
            "No %s custom variable for survey %s response %s; assuming survey taken by non-user" % (token_var, survey_id, response_id)
        )

class SurveyResponseHook(View):

    def head(self, request, *args, **kwargs):
        return HttpResponse('OK') # needed to register as Surveymonkey webhook target

    def get(self, request, *args, **kwargs):
        if settings.ALLOW_SURVEY_RESPONSE_HOOK_BYPASS:
            sr = SurveyResponse.objects.get(id=request.GET["cmtoken"])
            sr.status = ResponseStatus.COMPLETED
            sr.save()
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
            except JSONDecodeError:
                logger.error("Error decoding webhook request body as JSON: %s" % request.body)
            except KeyError:
                logger.error("Key error when processing webhook data: %s" % data)
            finally:
                raise
        else:
            logger.warning("Invalid POST to SurveyResponseHook")
            
        return HttpResponse('THX')
 
status_hook = csrf_exempt(SurveyResponseHook.as_view())
