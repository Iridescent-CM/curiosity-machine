from django.contrib.auth.models import User
from images.models import Image

def create_or_edit_user(data, user=None):
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
        if profile.age >= 13:
            profile.approved = True
    profile.birthday = data['birthday']
    profile.nickname = data['nickname']
    profile.city = data['city']
    if new_user or user.profile.is_student:
        profile.parent_first_name = data['parent_first_name']
        profile.parent_last_name = data['parent_last_name']
    if user.profile.is_mentor:
        profile.title = data['title']
        profile.employer = data['employer']
        profile.about_me = data['about_me']
        profile.about_research = data['about_research']
    if data['picture_filepicker_url']:
        profile.image = Image.from_source_with_job(data['picture_filepicker_url'])
    profile.save()
