from django.contrib.auth.models import User
from images.models import Image
from videos.models import Video
import requests
import json

def create_or_edit_user(data, user=None):
    new_user = False
    if not user:
        user = User()
        new_user = True

    user.email = data['email']
    
    if new_user:
        user.username = data['username']
        user.is_active = True
    if new_user or data['password']:
        user.set_password(data['password'])

    if data['first_name']:
        user.first_name = data['first_name']
    if data['last_name']:
        user.last_name = data['last_name']
    user.save()

    profile = user.profile
    profile.birthday = data['birthday']
    if data.get('is_student') is not None:
        profile.is_student = data.get('is_student')
    else:
        profile.is_student = profile.is_student or False
    if data.get('is_mentor') is not None:
        profile.is_mentor = data.get('is_mentor')
    else:
        profile.is_mentor = profile.is_mentor or False
    if new_user and profile.is_student:
        if profile.age >= 13:
            profile.approved = True
    profile.city = data['city']
    if user.profile.is_student:
        profile.parent_first_name = data['parent_first_name']
        profile.parent_last_name = data['parent_last_name']
    if user.profile.is_mentor:
        profile.title = data['title']
        profile.employer = data['employer']
        profile.expertise = data['expertise']
        if 'about_me' in data:
            profile.about_me = data['about_me']
        if 'about_research' in data:
            profile.about_research = data['about_research']

        if 'about_me_filepicker_url' in data and 'about_me_filepicker_mimetype' in data:
            if data['about_me_filepicker_mimetype'].startswith('image'):
                image = Image.from_source_with_job(data['about_me_filepicker_url'])
                profile.about_me_image_id = image.id
                profile.about_me_video_id = None

            elif data['about_me_filepicker_mimetype'].startswith('video'):
                video = Video.from_source_with_job(data['about_me_filepicker_url'])
                profile.about_me_image_id = None
                profile.about_me_video_id = video.id

        if 'about_research_filepicker_url' in data and 'about_research_filepicker_mimetype' in data:
            if data['about_research_filepicker_mimetype'].startswith('image'):
                image = Image.from_source_with_job(data['about_research_filepicker_url'])
                profile.about_research_image_id = image.id
                profile.about_research_video_id = None

            elif data['about_research_filepicker_mimetype'].startswith('video'):
                video = Video.from_source_with_job(data['about_research_filepicker_url'])
                profile.about_research_image_id = None
                profile.about_research_video_id = video.id

    if data['picture_filepicker_url']:
        profile.image = Image.from_source_with_job(data['picture_filepicker_url'])
    profile.save()
