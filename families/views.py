from django.shortcuts import render
from django.views.generic import TemplateView
from profiles.decorators import only_for_role
from profiles.models import UserRole

only_for_family = only_for_role(UserRole.family)

class HomeView(TemplateView):
    template_name = "families/home.html"

home = only_for_family(HomeView.as_view())
