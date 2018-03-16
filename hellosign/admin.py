from django.contrib import admin
from enumfields.admin import EnumFieldListFilter
from .models import *
from .updating import Updating

class SignatureAdmin(admin.ModelAdmin):
    list_display = ['id', 'template_id', 'user', 'status', 'created_at', 'updated_at']
    list_filter = [('status', EnumFieldListFilter)]
    readonly_fields = [
        'id',
        'template_id',
        'user',
        'created_at',
        'updated_at',
        'signature_request_id',
        'signature_id'
    ]
    search_fields = ['id', 'template_id', 'user__username']

    def save_model(self, request, obj, form, change):
        if not change:
            return super().save_model(request, obj, form, change)

        if form.has_changed():
            # it can only be status because of readonly_fields above,
            # Updating wants the original not the modified (FIXME?)
            Updating(Signature.objects.get(pk=obj.id), form.cleaned_data['status']).run()

admin.site.register(Signature, SignatureAdmin)
