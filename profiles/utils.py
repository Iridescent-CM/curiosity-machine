from django.shortcuts import render, get_object_or_404
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from django.forms.util import ErrorList
from profiles.models import Profile
from profiles.forms import JoinForm, ProfileEditForm
from django.db import transaction

def create_or_edit_user(request, data, user=None):
    new_user = False
    if not user:
        user = User()
        new_user = True

    user.email = data['email']
    user.first_name = data['first_name']
    if new_user:
        user.username = data['username']
        user.is_active = True
    if new_user or data['password']:
        user.set_password(data['password'])
    user.save()

    profile = user.profile
    if new_user:
        profile.is_mentor = False
    profile.birthday = data['birthday']
    profile.nickname = data['nickname']
    profile.city = data['city']
    if data['parent_first_name']:
        profile.parent_first_name = data['parent_first_name']
    if data['parent_last_name']:
        profile.parent_last_name = data['parent_last_name']
    profile.save()
