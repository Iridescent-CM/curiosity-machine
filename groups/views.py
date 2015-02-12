from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render
from .models import Group

@login_required
def groups(request):
	groups = request.user.profile.groups.all()
	return render(request, 'groups.html', {'groups': groups})

@login_required
def group(request, group_id): 
	group = request.user.profile.groups.filter(id=group_id).first()
	if not group: return Http404("No group for given query")
	return render(request, 'group.html', {'group': group})