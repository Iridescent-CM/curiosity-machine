from .templates import EmailTemplate
import logging

logger = logging.getLogger(__name__)

STUDENT = 'student'
MENTOR = 'mentor'
UNDERAGE_STUDENT = 'underage_student'
EDUCATOR = 'educator'
PARENT = 'parent'

def template_path(name, user_type):
    return '%s/%s' % (name, user_type)

def email_dict(tmpl, user_type, subject):
    return {'template': template_path(tmpl, user_type), 'subject': subject}

def email(recipients, subject, context, template, cc_recipients=None):
    email = EmailTemplate(recipients, subject, template, context, cc_recipients=cc_recipients)
    return email.deliver()

email_info = {
    #welcome
    'mentor_welcome': email_dict('welcome', MENTOR, 'Welcome to the Curiosity Machine!'),
    'educator_welcome': email_dict('welcome', EDUCATOR, 'Welcome to Curiosity Machine'),
    'parent_welcome': email_dict('welcome', PARENT, 'Welcome to Curiosity Machine!'),

    #activation
    'underage_student_activation_confirmation': email_dict('activation_confirmation', UNDERAGE_STUDENT, 'Your Child’s Curiosity Machine Account Is Now Active'),

    #encouragement
    'mentor_encouragement': email_dict('encouragement', MENTOR, 'New Students Projects on Curiosity Machine!'),

    #first project
    'student_first_project': email_dict('first_project', STUDENT, 'Success! Your Curiosity Machine Project Was Submitted'), 
    'underage_student_first_project': email_dict('first_project', UNDERAGE_STUDENT, 'Success! Your Child’s Curiosity Machine Project Was Submitted'),

    #mentor responded
    'student_mentor_responded': email_dict('mentor_responded', STUDENT, 'A Curiosity Machine Mentor Responded to Your Project'), 
    'underage_student_mentor_responded': email_dict('mentor_responded', UNDERAGE_STUDENT, "A Curiosity Machine Mentor Responded to Your Child's Project"),

    #module completed
    'mentor_module_completed': email_dict('module_completed', MENTOR, 'Get Started on Curiosity Machine!'),

    #project completion
    'student_project_completion': email_dict('project_completion', STUDENT, 'Publish Your Curiosity Machine Project'), 
    'underage_student_project_completion': email_dict('project_completion', UNDERAGE_STUDENT, 'Publish Your Child’s Curiosity Machine Project'),

    #publish
    'student_publish': email_dict('publish', STUDENT, 'Thanks for Sharing Your Curiosity Machine Project!'), 
    'underage_student_publish': email_dict('publish', UNDERAGE_STUDENT, 'Thanks for Sharing on Curiosity Machine!'),

    #student completed
    'mentor_student_completed': email_dict('student_completed', MENTOR, 'Your Student Completed Their project!'),

    #student responded
    'mentor_student_responded': email_dict('student_responded', MENTOR, 'Your Student Responded!'),

    #mentor's training task done
    'mentor_training_task_done': email_dict('training_task_done', MENTOR, 'You Completed Task!'),

    'mentor_training_task_done': email_dict('training_task_done', MENTOR, 'You Completed Task!'),
    #group invite
    'student_group_invite': email_dict('group_invite', STUDENT, 'You have been invited to join a group!'), 
    'underage_student_group_invite': email_dict('group_invite', UNDERAGE_STUDENT, 'You have been invited to join a group!'),
}

def determine_user_type(profile):
    user_type = None
    if profile.is_mentor:
        user_type = MENTOR
    elif profile.is_educator:
        user_type = EDUCATOR
    elif profile.birthday:
        if profile.is_underage():
            user_type = UNDERAGE_STUDENT
        else:
            user_type = STUDENT
    elif profile.is_parent:
        user_type = PARENT
    return user_type

def deliver_email(event_name, profile, **context):
    context.update({'profile': profile})

    user_type = determine_user_type(profile)
    if user_type is None:
        logger.warn("Unable to determine user type for email event: {}, username: {}".format(event_name, profile.user.username))
        return None
    key = "_".join([user_type, event_name])
    try:
        info = email_info[key]
        if profile.user.email:
            return email([profile.user.email], context.get('subject', info['subject']), context, info['template'], context.get('cc', None))
        else:
            logger.info("No email address; email not sent for event: {}, type: {}, username: {}".format(event_name, user_type, profile.user.username))
    except KeyError:
        logger.warn("No email defined for event: {}, type: {}, username: {}".format(event_name, user_type, profile.user.username))
