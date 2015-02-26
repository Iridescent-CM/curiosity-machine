from django.shortcuts import render
from django.http import HttpResponse
import csv
import datetime
import tempfile
from challenges.models import Progress, Stage
from cmcomments.models import Comment
from .forms import AnalyticsForm
from django.core.exceptions import PermissionDenied
from tsl.models import Answer
from videos.models import Mime

def analytics(request):
    if not request.user.has_perms(['auth.change_user', 'cmcomments.change_comment', 'challenges.change_progress']):
        raise PermissionDenied
    if request.GET:
        form = AnalyticsForm(data=request.GET)
        if form.is_valid():
            return generate_analytics(form.cleaned_data['start_date'], form.cleaned_data['end_date'])
    else:
        form = AnalyticsForm()
    return render(request, 'analytics.html', {'analytics_form': form})

def generate_analytics(start_date, end_date):
    with tempfile.TemporaryFile(mode='w+') as fp:
        writer = csv.writer(fp)
        writer.writerow([
            "User Id",
            "Username",
            "User Type",
            "Action Type",
            "Stage",
            "Timestamp",
            "Challenge Id",
            "Challenge Learner Id",
            "Challenge Mentor Id",
            "Text",
            "Video/Image"
        ])

        progresses = Progress.objects.select_related('student')

        # Start Building
        started = progresses.filter(started__gte=start_date, started__lte=end_date)
        for progress in started:
            writer.writerow([
                progress.student_id,
                progress.student.username,
                "learner",
                "start building",
                "",
                progress.started.strftime('%Y-%m-%d %H:%M:%S'),
                progress.challenge_id,
                progress.student_id,
                progress.mentor_id,
                "",
                ""
            ])

        # Set to Reflection
        approved = progresses.filter(approved__gte=start_date, approved__lte=end_date)
        for progress in approved:
            writer.writerow([
                progress.student_id,
                progress.student.username,
                "learner",
                "sent to reflection",
                "",
                progress.approved.strftime('%Y-%m-%d %H:%M:%S'),
                progress.challenge_id,
                progress.student_id,
                progress.mentor_id,
                "",
                ""
            ])

        # Comments
        comments = Comment.objects.filter(
            created__gte=start_date,
            created__lte=end_date,
            challenge_progress=progresses
        ).select_related(
            'image',
            'video',
            'user__profile',
            'challenge_progress'
        ).prefetch_related(
            'video__encoded_videos'
        )

        for comment in comments:
            if comment.video:
                video_url = comment.video.url
                for video in comment.video.encoded_videos.all():
                    if video.mime_type == Mime.mp4.value:
                        video_url = video.url
            writer.writerow([
                comment.user_id,
                comment.user.username,
                "mentor" if comment.user.profile.is_mentor else "learner",
                "video" if comment.video else ("image" if comment.image else "text"),
                Stage(comment.stage).name,
                comment.created.strftime('%Y-%m-%d %H:%M:%S'),
                comment.challenge_progress.challenge_id,
                comment.challenge_progress.student_id,
                comment.challenge_progress.mentor_id,
                comment.text,
                video_url if comment.video else (comment.image.url if comment.image else "")
            ])

        # TSL Answers
        answers = Answer.objects.filter(
            created__gte=start_date,
            created__lte=end_date
        ).select_related(
            'user',
            'user__profile',
            'video',
            'image',
            'question'
        ).prefetch_related(
            'video__encoded_videos'
        )
        for answer in answers:
            if answer.video:
                video_url = answer.video.url
                for video in answer.video.encoded_videos.all():
                    if video.mime_type == Mime.mp4.value:
                        video_url = video.url
            array = [
                answer.user_id,
                answer.user.username,
                "mentor" if answer.user.profile.is_mentor else "learner",
                "tsl video" if answer.video else ("tsl image" if answer.image else "tsl text"),
                None,
                answer.created.strftime('%Y-%m-%d %H:%M:%S'),
                answer.question.id,
                answer.user_id,
                None,
                answer.answer_text,
                video_url if answer.video else (answer.image.url if answer.image else "")
            ]
            writer.writerow(array)

        fp.seek(0)
        response = HttpResponse(fp, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Analytics %s to %s.csv' % (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        return response
