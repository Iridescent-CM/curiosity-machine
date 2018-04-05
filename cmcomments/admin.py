from django.contrib import admin
from .models import Comment
from videos.models import Video
from images.models import Image


class CommentAdmin(admin.ModelAdmin):
    model = Comment
    list_display = ('user', 'text', 'created')
    raw_id_fields = ['challenge_progress', 'user', 'image', 'video']

    def get_form(self, request, obj=None, **kwargs):
        request._obj_ = obj
        return super(CommentAdmin, self).get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.method == 'GET':
            if db_field.name == 'video':
                if request._obj_ is not None and request._obj_.video is not None:
                    kwargs["queryset"] = Video.objects.filter(source_url = request._obj_.video.source_url)  
                else:
                    kwargs["queryset"] = Video.objects.none()

            if db_field.name == 'image':
                if request._obj_ is not None and request._obj_.image is not None:
                    kwargs["queryset"] = Image.objects.filter(source_url = request._obj_.image.source_url)  
                else:
                    kwargs["queryset"] = Image.objects.none()
        return super(CommentAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Comment,CommentAdmin)
