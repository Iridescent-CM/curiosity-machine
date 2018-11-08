from django.shortcuts import render
from django.views.generic import *
from .forms import *
from .models import *

class SignSlipView(CreateView):
    model = PermissionSlip
    form_class = PermissionSlipSignatureForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.account = self.request.user
        obj.save()
        self.object = obj
        return super().form_valid(form)
