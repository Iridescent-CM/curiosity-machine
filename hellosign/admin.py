from django.contrib import admin
from .models import *

class SignatureAdmin(admin.ModelAdmin):
    pass

admin.site.register(Signature, SignatureAdmin)
