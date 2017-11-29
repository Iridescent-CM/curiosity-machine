from django.conf import settings

def emails(request):
    return {
        'emails': {
            'mentor_interest': settings.MENTOR_INTEREST_EMAIL,
            'contact': settings.CONTACT_EMAIL,
        }
    }
