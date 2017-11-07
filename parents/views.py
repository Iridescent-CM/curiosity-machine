from curiositymachine.views.generic import ToggleView, SoftDeleteView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.functional import lazy
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from profiles.decorators import only_for_role
from .decorators import *
from .forms import *
from .models import *

class CreateProfileView(CreateView):
    model = ParentProfile
    form_class = NewParentProfileForm
    success_url = lazy(reverse, str)("parents:home")

    def get_initial(self):
        initial = super().get_initial()
        initial.update({
            "user": self.request.user
        })
        return initial

create = CreateProfileView.as_view()

class EditProfileView(UpdateView):
    model = ParentProfile
    fields = '__all__'

    def get_object(self, queryset=None):
        return self.request.user.parentprofile

edit = EditProfileView.as_view()

class HomeView(TemplateView):
    template_name = "parents/home.html"

    def get_context_data(self, **kwargs):
        children = ParentConnection.objects.filter(parent_profile=self.request.user.parentprofile, removed=False)
        trainings = [
            {
                "title": "The Creative Parent's Toolbox",
                "imagePath": "profiles/01_forces-and-growth-mindset.png",
                "description": "Presentations that cover basic physics and learning mindsets",
                "link": "/parent-training-intro-series/"
            },
            {
                "title": "La Caja de herramientas del Padre Creativo",
                "imagePath": "profiles/01_forces-and-growth-mindset.png",
                "description": "Entrenamiento que cubre los conceptos básicos de la física y cómo cultivar una mentalidad de aprendizaje",
                "link": "/parent-training-intro-series-sp/"
            },
        ]
        return super().get_context_data(
            **kwargs,
            user=self.request.user,
            children=children,
            trainings=trainings,
        )

home = login_required(HomeView.as_view())

class NewConnectionView(UpdateView):
    model = ParentProfile
    form_class = ConnectForm
    success_url = lazy(reverse, str)('parents:home')
    template_name = "parents/connect/connect_form.html"

    def get_object(self, queryset=None):
        return self.request.user.parentprofile

connect = only_for_role('parent')(NewConnectionView.as_view())

class ChildView(DetailView):
    model = ParentConnection
    pk_url_kwarg = 'connection_id'
    template_name = 'parents/connect/child_detail.html'
    context_object_name = 'connection'

view_child = active_connected_parent_only(ChildView.as_view())

def reverse_with_anchor(view, anchor):
    return "{}#{}".format(reverse(view), anchor)

class ToggleConnectionView(ToggleView):
    model = ParentConnection
    pk_url_kwarg = 'connection_id'
    success_url = lazy(reverse_with_anchor, str)('profiles:home', 'parents')

    def toggle(self, obj):
        obj.active = not obj.active
        obj.save(update_fields=['active'])
        if obj.active:
            messages.success(self.request, "{} can now see your progress".format(obj.parent_profile.user.username))
        else:
            messages.success(self.request, "{} can no longer see your progress".format(obj.parent_profile.user.username))

toggle_connection = connected_child_only(ToggleConnectionView.as_view())

class DeleteConnectionView(SoftDeleteView):
    model = ParentConnection
    pk_url_kwarg = 'connection_id'
    success_url = lazy(reverse, str)('profiles:home')
    deletion_field = 'removed'

    def get_template_names(self):
        return ["parents/connect/%s_confirm_delete.html" % self.request.user.extra.user_type]

remove_connection = connected_only(DeleteConnectionView.as_view())
