from debug_toolbar.middleware import show_toolbar
from django.conf import settings

def show_toolbar(request):
    return show_toolbar and settings.DEBUG_TOOLBAR
