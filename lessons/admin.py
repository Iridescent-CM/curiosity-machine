from django.contrib import admin
from django import forms
from django_ace import AceWidget
from .models import *

ACEWIDTH = "800px"

class LessonAdminForm(forms.ModelForm):
    class Meta:
        model = Lesson
        exclude = []
        widgets = {
            'inspiration': AceWidget(mode="html", width=ACEWIDTH, wordwrap=True),
            'plan': AceWidget(mode="html", width=ACEWIDTH),
            'build': AceWidget(mode="html", width=ACEWIDTH),
            'reflect': AceWidget(mode="html", width=ACEWIDTH),
            'further': AceWidget(mode="html", width=ACEWIDTH),
        }
        js = ('django_ace/widget.js',)

class LessonAdmin(admin.ModelAdmin):
    form = LessonAdminForm
    save_as = True
    save_on_top = True
    list_display = ('id', 'title')

admin.site.register(Lesson, LessonAdmin)
