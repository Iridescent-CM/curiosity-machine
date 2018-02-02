from django.utils.timezone import now

# maybe put this kind of shit into static methods on the model? 
def check(user):
    profile = user.familyprofile
    if profile.check_full_access() and not profile.welcomed:
        profile.welcomed = now()
        profile.save(update_fields=['welcomed'])
