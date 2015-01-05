from django.contrib.auth.models import User
from images.models import Image
from videos.models import Video
import requests
import json

def filepicker_meta(url):
    return json.loads(requests.get("/".join([url, 'metadata'])).text)

def type_from_filepicker(url):
    meta = filepicker_meta(url)
    if "image" in meta['mimetype']:
        return 'image'
    elif "video" in meta['mimetype']:
        return 'video'
    else:
        return None

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
    if data.get('is_mentor') is not None:
        profile.is_mentor = data.get('is_mentor')
    else:
        profile.is_mentor = profile.is_mentor or False
    if new_user and not profile.is_mentor:
        if profile.age >= 13:
            profile.approved = True
    profile.city = data['city']
    if user.profile.is_student:
        profile.parent_first_name = data['parent_first_name']
        profile.parent_last_name = data['parent_last_name']
    if user.profile.is_mentor:
        profile.title = data['title']
        profile.employer = data['employer']
        profile.about_me = data['about_me']
        profile.about_research = data['about_research']

        if data['about_me_filepicker_url']:
            if type_from_filepicker(data['about_me_filepicker_url']) == 'image':
                if data['about_me_filepicker_url']:
                    image = Image.from_source_with_job(data['about_me_filepicker_url'])
                    data['about_me_image_id'] = image.id
                    data['about_me_video_id'] = None

            elif type_from_filepicker(data['about_me_filepicker_url']) == 'video':
                if data['about_me_filepicker_url']:
                    video = Video.from_source_with_job(data['about_me_filepicker_url']) if data['about_me_filepicker_url'] else None
                    data['about_me_image_id'] = None
                    data['about_me_video_id'] = video.id

        if data['about_research_filepicker_url']:
            if type_from_filepicker(data['about_research_filepicker_url']) == 'image':
                if data['about_research_filepicker_url']:
                    image = Image.from_source_with_job(data['about_research_filepicker_url'])
                    data['about_research_image_id'] = image.id
                    data['about_research_video_id'] = None

            elif type_from_filepicker(data['about_research_filepicker_url']) == 'video':
                if data['about_research_filepicker_url']:
                    video = Video.from_source_with_job(data['about_research_filepicker_url']) if data['about_research_filepicker_url'] else None
                    data['about_research_image_id'] = None
                    data['about_research_video_id'] = video.id

    if data['picture_filepicker_url']:
        profile.image = Image.from_source_with_job(data['picture_filepicker_url'])
    profile.save()
