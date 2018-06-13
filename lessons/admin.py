from django.contrib import admin
from django import forms
from django_ace import AceWidget
from .models import *

ACECONFIG = {
    "width": "800px",
    "wordwrap": True
}

class LessonAdminForm(forms.ModelForm):
    class Meta:
        model = Lesson
        exclude = []
        widgets = {
            'inspiration': AceWidget(mode="html", **ACECONFIG),
            'plan': AceWidget(mode="html", **ACECONFIG),
            'build': AceWidget(mode="html", **ACECONFIG),
            'reflect': AceWidget(mode="html", **ACECONFIG),
            'further': AceWidget(mode="html", **ACECONFIG),
        }

    class Media:
        js = ('js/ace_widget.js',)

class LessonAdmin(admin.ModelAdmin):
    form = LessonAdminForm
    save_as = True
    save_on_top = True
    list_display = ('id', 'title')

admin.site.register(Lesson, LessonAdmin)
