from django.shortcuts import render
from django.http import HttpResponse
import csv
import datetime
import tempfile
from challenges.models import Progress, Stage
from .forms import AnalyticsForm
from django.core.exceptions import PermissionDenied

def statistics(request):
    if not request.user.has_perms(['auth.change_user', 'cmcomments.change_comment', 'challenges.change_progress']):
        raise PermissionDenied
    
    return render(request, 'statistics.html')