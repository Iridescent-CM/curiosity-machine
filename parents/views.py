from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.functional import lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
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
