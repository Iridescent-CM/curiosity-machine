from django.conf import settings

def feature_flags(request):
    return { 'flags': settings.FEATURE_FLAGS }

