from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from .api import Surveymonkey
from .models import *
import base64
import django_rq
import hashlib
import hmac
import json
import requests

api = Surveymonkey()

def update_status(survey_id, response_id):
    res = api.get("surveys/%s/responses/%s" % (survey_id, response_id))
    # error handling?

    data = res.json()
    token = data.get('custom_variables').get(settings.SURVEYMONKEY_TOKEN_VAR, None)
    if token:
        status = ResponseStatus[data.get('response_status').upper()]

        sr = SurveyResponse.objects.get(id=token)
        sr.status = status
        sr.save()

class SurveyResponseHook(View):

    def head(self, request, *args, **kwargs):
        return HttpResponse('OK') # needed to register as Surveymonkey webhook target

    def post(self, request, *args, **kwargs):
        if api.valid(request.body, request.META['HTTP_SM_SIGNATURE'].encode("ascii")):
            data = json.loads(request.body)
            survey_id = data.get('filter_id')
            response_id = data.get('object_id')
            # maybe check filter_type and object_type?
            django_rq.enqueue(update_status, survey_id, response_id)
            
        return HttpResponse('THX')
 
status_hook = csrf_exempt(SurveyResponseHook.as_view())
