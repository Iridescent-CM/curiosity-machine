from django.contrib import admin
from .models import Module, Comment, Task
from django.contrib.auth.models import User
from videos.models import Video
from images.models import Image
from cmcomments.admin import CommentAdmin

class TaskAdmin(admin.ModelAdmin):
    filter_horizontal = ('mentors_done',)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "mentors_done":
            kwargs["queryset"] = User.objects.filter(profile__is_mentor=True)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

admin.site.register(Module)
admin.site.register(Task, TaskAdmin)
admin.site.register(Comment, CommentAdmin)
