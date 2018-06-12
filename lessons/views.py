from collections import OrderedDict
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView
from rest_framework import serializers
from rest_framework import viewsets
from .models import *

LESSON_NAV = OrderedDict({
    "inspiration": {
        "text": "Inspiration",
    },
    "plan": {
        "text": "Plan",
    },
    "build": {
        "text": "Build Test Redesign"
    },
    "reflect": {
        "text": "Reflect"
    },
    "further": {
        "text": "Further learning"
    }
})

class PageView(DetailView):
    model = Lesson
    context_object_name = "lesson"

    def get(self, request, *args, **kwargs):
        page = kwargs.pop('page')
        self.page = page.lower()
        if self.page not in LESSON_NAV:
            raise Http404

        return super().get(request, *args, **kwargs)

    def get_template_names(self):
        return ["lessons/%s.html" % self.page, "lessons/base.html",]

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            subnav=LESSON_NAV,
            active=self.page,
            content=getattr(self.object, self.page, None)
        )

show_page = staff_member_required(PageView.as_view())

# class UploadSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Upload
#         fields = ('id', 'text', 'object_id', 'content_type', 'author')
#
# class UploadViewSet(viewsets.ModelViewSet):
#     serializer_class = UploadSerializer
#     permission_classes = []
#
#     def get_queryset(self):
#         lesson_type = ContentType.objects.get_for_model(Lesson)
#         return Upload.objects.filter(
#             author=self.request.user,
#             content_type__pk=lesson_type.id,
#             object_id=self.kwargs['lesson_pk']
#         )
