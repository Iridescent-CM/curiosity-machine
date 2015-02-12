from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from .models import Group

def groups(request):
	groups = Group.objects.all()
	return render(request, 'groups.html', {'groups': groups})

def group(request, group_id): 
	group = get_object_or_404(Group, id=group_id)
	return render(request, 'group.html', {'group': group})


# @login_required
# def user_groups(request):
# 	groups = request.user.profile.groups.all()
# 	return render(request, 'groups.html', {'groups': groups})

# @login_required
# def user_group(request, group_id): 
# 	group = request.user.profile.groups.filter(id=group_id).first()
# 	if not group: return Http404("No group for given query")
# 	return render(request, 'group.html', {'group': group})