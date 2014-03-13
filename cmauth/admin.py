from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

class CMUserChangeForm(UserChangeForm):
    def __init__(self, *args, **kargs):
        super(CMUserChangeForm, self).__init__(*args, **kargs)
        del self.fields['username']

    class Meta:
        model = User

class CMUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kargs):
        super(CMUserCreationForm, self).__init__(*args, **kargs)
        del self.fields['username']

    class Meta:
        model = User
        fields = ("email",)

class CMUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'role',
                                       'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    search_fields = ('email', 'first_name', 'last_name')
    list_display = ('email', 'role', 'first_name', 'last_name', 'is_staff')
    form = CMUserChangeForm
    add_form = CMUserCreationForm
    ordering = ('email',)

admin.site.register(User, CMUserAdmin)

