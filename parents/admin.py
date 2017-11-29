from django.contrib import admin
from .models import *

class ParentConnectionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'parent', 'parent_email', 'child', 'child_email', 'active', 'removed']
    list_filter = ['active', 'removed']
    search_fields = [
        'parent_profile__user__username',
        'child_profile__user__username',
        'parent_profile__user__email',
        'child_profile__user__email'
    ]

    def parent(self, obj):
        return obj.parent_profile.user.username
    parent.admin_order_field = 'parent_profile__user__username'

    def parent_email(self, obj):
        return obj.parent_profile.user.email
    parent.admin_order_field = 'parent_profile__user__email'

    def child(self, obj):
        return obj.child_profile.user.username
    child.admin_order_field = 'child_profile__user__username'

    def child_email(self, obj):
        return obj.child_profile.user.email
    child.admin_order_field = 'child_profile__user__email'

admin.site.register(ParentConnection, ParentConnectionAdmin)
