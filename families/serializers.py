from images.models import Image
from rest_framework import serializers
from .models import *

class ChecklistSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        data = {
            k: getattr(obj, k)
            for k in [
                'challenges_completed',
                'complete',
            ]
        }
        data['items'] = {
            k: getattr(obj, k)
            for k in [
                'enough_challenges_completed',
                'email_unique',
                'email_verified',
                'post_survey_taken',
                'family_confirmed_all_listed',
            ]
        }
        return data

