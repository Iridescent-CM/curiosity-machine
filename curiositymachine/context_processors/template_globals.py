from django.conf import settings

def template_globals(request):
    return {
        "SITE_MESSAGE": settings.SITE_MESSAGE,
        "SITE_MESSAGE_LEVEL": settings.SITE_MESSAGE_LEVEL,
        "SITE_URL": settings.SITE_URL,
        "ROLLBAR_CLIENT_SIDE_ACCESS_TOKEN": settings.ROLLBAR_CLIENT_SIDE_ACCESS_TOKEN,
        "ROLLBAR_ENV": settings.ROLLBAR_ENV,
        "ROLLBAR_VERBOSE": settings.ROLLBAR_VERBOSE,
        "FILEPICKER_API_KEY": settings.FILEPICKER_API_KEY,
    }

