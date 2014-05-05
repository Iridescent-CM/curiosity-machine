from django.shortcuts import render
from django.http import HttpResponse
import csv
import datetime
import io
from challenges.models import Progress, Stage
from .forms import AnalyticsForm

def analytics(request):
    if not request.user.has_perms(['auth.change_user', 'cmcomments.change_comment', 'challenges.change_progress']):
        return HttpResponse("You cannot view this page.", status=403)
    if request.GET:
        form = AnalyticsForm(data=request.GET)
        if form.is_valid():
            return generate_analytics(form.cleaned_data['start_date'], form.cleaned_data['end_date'])
    else:
        form = AnalyticsForm()
    return render(request, 'analytics.html', {'analytics_form': form})

def generate_analytics(start_date, end_date):
    f = io.StringIO()
    writer = csv.writer(f)
    writer.writerow(["User Id", "Username", "User Type", "Action Type", "Stage", "Timestamp", "Challenge Id", "Challenge Learner Id", "Challenge Mentor Id", "Text", "Video/Image"])

    progresses = Progress.objects.all()

    # Start Building
    started = progresses.filter(started__gte=start_date, started__lte=end_date)
    for progress in started:
        writer.writerow([progress.student_id, progress.student.username, "learner", "start building", "", progress.started.strftime('%Y-%m-%d %H:%M:%S'), progress.challenge_id, 
            progress.student_id, progress.mentor_id, "", ""])

    # Set to Reflection
    approved = progresses.filter(approved__gte=start_date, approved__lte=end_date)
    for progress in approved:
        writer.writerow([progress.student_id, progress.student.username, "learner", "sent to reflection", "", progress.approved.strftime('%Y-%m-%d %H:%M:%S'), progress.challenge_id, 
            progress.student_id, progress.mentor_id, "", ""])

    # Comments
    comments = []
    for progress in progresses:
        comments.extend(progress.comments.filter(created__gte=start_date, created__lte=end_date))
    for comment in comments:
        if comment.video:
            writer.writerow([comment.user_id, comment.user.username, "mentor" if comment.user.profile.is_mentor else "learner", 
                "video", Stage(comment.stage).name, comment.created.strftime('%Y-%m-%d %H:%M:%S'), comment.challenge_progress.challenge_id, comment.challenge_progress.student_id, 
                comment.challenge_progress.mentor_id, comment.text, comment.video.url])
        elif comment.image:
            writer.writerow([comment.user_id, comment.user.username, "mentor" if comment.user.profile.is_mentor else "learner", 
                "image", Stage(comment.stage).name, comment.created.strftime('%Y-%m-%d %H:%M:%S'), comment.challenge_progress.challenge_id, comment.challenge_progress.student_id, 
                comment.challenge_progress.mentor_id, comment.text, comment.image.url])
        else:
            writer.writerow([comment.user_id, comment.user.username, "mentor" if comment.user.profile.is_mentor else "learner", 
                "text", Stage(comment.stage).name, comment.created.strftime('%Y-%m-%d %H:%M:%S'), comment.challenge_progress.challenge_id, comment.challenge_progress.student_id, 
                comment.challenge_progress.mentor_id, comment.text])

    f.seek(0)
    response = HttpResponse(f, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Analytics %s to %s.csv' % (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    return response
