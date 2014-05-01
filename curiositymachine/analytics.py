from django.shortcuts import render
from django.http import HttpResponse
import xlwt
import datetime
import io
from challenges.models import Progress, Stage
from .forms import AnalyticsForm

def analytics(request):
    if request.method == 'POST':
        form = AnalyticsForm(data=request.POST)
        if form.is_valid():
            return generate_analytics(form.cleaned_data['actions'], form.cleaned_data['start_date'], form.cleaned_data['end_date'])
    else:
        form = AnalyticsForm()
    return render(request, 'analytics.html', {'analytics_form': form})

def generate_analytics(actions, start_date, end_date):
    f = io.BytesIO()
    book = xlwt.Workbook(encoding="utf-8")
    sheet1 = book.add_sheet("Sheet 1")
    sheet1.write(0, 0, "User Id")
    sheet1.write(0, 1, "Username")
    sheet1.write(0, 2, "User Type")
    sheet1.write(0, 3, "Action Type")
    sheet1.write(0, 4, "Stage")
    sheet1.write(0, 5, "Timestamp")
    sheet1.write(0, 6, "Challenge Id")
    sheet1.write(0, 7, "Challenge Learner Id")
    sheet1.write(0, 8, "Challenge Mentor Id")
    sheet1.write(0, 9, "Text")
    sheet1.write(0, 10, "Video/Image")
    
    line = 1

    progresses = Progress.objects.all()

    if 'Start Building' in actions:
        started = progresses.filter(started__gte=start_date, started__lte=end_date)
        for progress in started:
            sheet1.write(line, 0, progress.student_id)
            sheet1.write(line, 1, progress.student.username)
            sheet1.write(line, 2, "learner")
            sheet1.write(line, 3, "start building")
            sheet1.write(line, 4, "")
            sheet1.write(line, 5, progress.started.strftime('%Y-%m-%d %H:%M:%S'))  #2011-03-27 01:30:00
            sheet1.write(line, 6, progress.challenge_id)
            sheet1.write(line, 7, progress.student_id)
            sheet1.write(line, 8, progress.mentor_id)
            sheet1.write(line, 9, "")
            sheet1.write(line, 10, "")
            print('Started: user_id %s, challenge_id %s' % (progress.student_id, progress.challenge_id))
            line += 1

    if 'Set to Reflection' in actions:
        approved = progresses.filter(approved__gte=start_date, approved__lte=end_date)
        for progress in approved:
            sheet1.write(line, 0, progress.student_id)
            sheet1.write(line, 1, progress.student.username)
            sheet1.write(line, 2, "learner")
            sheet1.write(line, 3, "sent to reflection")
            sheet1.write(line, 4, "")
            sheet1.write(line, 5, progress.approved.strftime('%Y-%m-%d %H:%M:%S'))  #2011-03-27 01:30:00
            sheet1.write(line, 6, progress.challenge_id)
            sheet1.write(line, 7, progress.student_id)
            sheet1.write(line, 8, progress.mentor_id)
            sheet1.write(line, 9, "")
            sheet1.write(line, 10, "")
            print('Approved: user_id %s, challenge_id %s' % (progress.student_id, progress.challenge_id))
            line += 1

    if 'Comments' in actions:
        comments = []
        for progress in progresses:
            comments.extend(progress.comments.filter(created__gte=start_date, created__lte=end_date))
        for comment in comments:
            sheet1.write(line, 0, comment.user_id)
            sheet1.write(line, 1, comment.user.username)
            sheet1.write(line, 2, "mentor" if comment.user.profile.is_mentor else "learner")
            sheet1.write(line, 3, "video" if comment.video else ("image" if comment.image else "text"))
            sheet1.write(line, 4, Stage(comment.stage).name)
            sheet1.write(line, 5, comment.created.strftime('%Y-%m-%d %H:%M:%S'))  #2011-03-27 01:30:00
            sheet1.write(line, 6, comment.challenge_progress.challenge_id)
            sheet1.write(line, 7, comment.challenge_progress.student_id)
            sheet1.write(line, 8, comment.challenge_progress.mentor_id)
            sheet1.write(line, 9, comment.text)
            if comment.video:
                sheet1.write(line, 10, comment.video.url)
            elif comment.image:
                sheet1.write(line, 10, comment.image.url)
            print('Comment: user_id %s, challenge_id %s' % (comment.user_id, comment.challenge_progress.challenge_id))
            line += 1

    book.save(f)
    f.seek(0)
    response = HttpResponse(f, content_type='text/xls')
    response['Content-Disposition'] = 'attachment; filename=Analytics %s to %s.xls' % (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    return response
