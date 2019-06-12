from django.conf import settings

def emails(request):
    return {
        'emails': {
            'contact': settings.CONTACT_EMAIL,
        }
    }
