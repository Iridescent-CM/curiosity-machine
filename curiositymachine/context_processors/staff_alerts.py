from challenges.models import Example

def staff_alerts(request):
    if request.user.is_authenticated() and request.user.is_staff:
        return {
            "staff_alerts": {
                "pending_examples": Example.objects.filter(approved__isnull=True).count()
            }
        }
    else:
        return {}
