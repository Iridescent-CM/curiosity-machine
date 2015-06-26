from django.shortcuts import render
from django.contrib import auth, messages
from django.http import HttpResponseRedirect, HttpResponse
from django.db import transaction
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from curiositymachine.decorators import feature_flag
from django.core.urlresolvers import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from curiositymachine.views.generic import SoftDeleteView
from django.utils.functional import lazy
from profiles.forms import parent as forms
from profiles.models import ParentConnection, Profile
from profiles.decorators import parents_only, connected_parent_only, active_connected_parent_only
from django.utils.decorators import method_decorator

@transaction.atomic
@feature_flag('enable_parents')
def join(request):
    if request.method == 'POST':
        form = forms.ParentUserAndProfileForm(data=request.POST, prefix="parent")
        if form.is_valid():
            user = form.save()
            user = auth.authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            auth.login(request, user)
            return HttpResponseRedirect('/')
        else:
            return render(request, 'profiles/parent/join.html', {
                'form': form
            })
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('profiles:home'))
        else:
            form = forms.ParentUserAndProfileForm(prefix="parent")
            return render(request, 'profiles/parent/join.html', {
                'form': form
            })

@login_required
@feature_flag('enable_parents')
def home(request):
    children = ParentConnection.objects.filter(parent_profile=request.user.profile, removed=False)
    trainings = [
        {
            "title": "Unit 1",
            "imagePath": "profiles/01_forces-and-growth-mindset.png",
            "description": "Forces & Growth Mindset"
        },
        {
            "title": "Unit 2",
            "imagePath": "profiles/02_motion.png",
            "description": "Motion & Open-Ended Questions"
        },
        {
            "title": "Unit 3",
            "imagePath": "profiles/03_structural-strength.png",
            "description": "Structural Strength & EDP"
        },
        {
            "title": "Unit 4",
            "imagePath": "profiles/04_forces-of-flight.png",
            "description": "Forces of Flight & Persistence"
        },
        {
            "title": "Unit 5",
            "imagePath": "profiles/05_electricity-and-gender.png",
            "description": "Electricity & Gender Biases"
        },
        {
            "title": "Unit 6",
            "imagePath": "profiles/06_cognitive-apprenticeship.png",
            "description": "Power & Cognitive Apprenticeship"
        },
        {
            "title": "Unit 7",
            "imagePath": "profiles/07_family-course.png",
            "description": "How to Organize a Family Course"
        },
    ]
    return render(request, "profiles/parent/home.html", {
        "user": request.user,
        "children": children,
        "trainings": trainings
    })

@login_required
@transaction.atomic
@feature_flag('enable_parents')
def profile_edit(request):
    if request.method == 'POST':
        form = forms.ParentUserAndProfileForm(data=request.POST, instance=request.user, prefix="parent")
        if form.is_valid():
            form.save();
            messages.success(request, 'Profile has been updated.')
        else:
            messages.error(request, 'Correct errors below.')
    else:
        form = forms.ParentUserAndProfileForm(instance=request.user, prefix="parent")

    return render(request, 'profiles/parent/profile_edit.html', {
        'form': form
    })

class ParentConnectionCreateView(UpdateView):
    model = Profile
    form_class = forms.ConnectForm
    success_url = lazy(reverse, str)('profiles:home')
    template_name = "profiles/parent/connect_form.html"

    @method_decorator(login_required)
    @method_decorator(parents_only)
    @method_decorator(feature_flag('enable_parents'))
    def dispatch(self, *args, **kwargs):
        return super(ParentConnectionCreateView, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        res = super(ParentConnectionCreateView, self).form_valid(form)
        already_connected = [pair[0].child_profile.user.username for pair in form.saved]
        #TODO use messages to communicate already connected?
        return res

class ChildDetailView(DetailView):
    model = ParentConnection
    pk_url_kwarg = 'connection_id'
    template_name = 'profiles/parent/child_detail.html'
    context_object_name = 'connection'

    @method_decorator(login_required)
    @method_decorator(active_connected_parent_only)
    @method_decorator(feature_flag('enable_parents'))
    def dispatch(self, *args, **kwargs):
            return super(ChildDetailView, self).dispatch(*args, **kwargs)

class ParentConnectionDeleteView(SoftDeleteView):
    model = ParentConnection
    pk_url_kwarg = 'connection_id'
    template_name = 'profiles/parent/parentconnection_confirm_delete.html'
    success_url = lazy(reverse, str)('profiles:home')
    deletion_field = 'removed'

    @method_decorator(login_required)
    @method_decorator(connected_parent_only)
    @method_decorator(feature_flag('enable_parents'))
    def dispatch(self, *args, **kwargs):
            return super(ParentConnectionDeleteView, self).dispatch(*args, **kwargs)

remove_connection = ParentConnectionDeleteView.as_view()
