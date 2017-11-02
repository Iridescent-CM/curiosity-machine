from allauth.account.forms import LoginForm
from profiles.forms import mentor, educator, parent, student

def login_and_join_forms(request):
    return {
        'login_form': LoginForm(),
        'join_form': student.StudentUserAndProfileForm(prefix="student"),
        'mentor_join_form': mentor.MentorUserAndProfileForm(prefix="mentor"),
        'educator_join_form': educator.EducatorUserAndProfileForm(prefix="educator"),
        'parent_join_form': parent.ParentUserAndProfileForm(prefix="parent")
    }


