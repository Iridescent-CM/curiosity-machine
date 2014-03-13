from django.contrib import admin
from .models import Challenge, Step, Theme, Material, Question

class ChallengeAdmin(admin.ModelAdmin):
    filter_horizontal = ('steps', 'material', 'questions')


admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(Step,)
admin.site.register(Theme,)
admin.site.register(Material,)
admin.site.register(Question,)
