from django.db import models
from .templates import EmailTemplate

#helpers here
class Notification(object):
    STUDENT = 'student'
    MENTOR = 'mentor'
    UNDERAGE_STUDENT = 'underage_student'

    def __init__(self, template):
        self.template = template

    #template helpers
    def template_for(self, user_type):
        return '/'.join((self.template, user_type))

    def student_template(self):
        return self.template_for(self.STUDENT)

    def underage_student_template(self):
        return self.template_for(self.UNDERAGE_STUDENT)

    def mentor_template(self):
        return self.template_for(self.MENTOR)

    #email helpers
    def email(self, recipients, subject, context, template):
        email = EmailTemplate(recipients, subject, template, context)
        return email.deliver()

    def email_mentor(self, recipients, subject, context = {}):
        return self.email(recipients, subject, context, self.mentor_template())

    def email_student(self, recipients, subject, context = {}):
        return self.email(recipients, subject, context, self.student_template())

    def email_underage_student(self, recipients, subject, context = {}):
        return self.email(recipients, subject, context, self.underage_student_template())

    def deliver_email(self, *args, **kwargs):
        profile = args[0]
        methods = dir(self)
        if profile.is_mentor:
            if 'deliver_to_mentor' in methods:
                return self.deliver_to_mentor(*args, **kwargs)
        elif profile.is_underage():
            if 'deliver_to_underage_student' in methods:
                return self.deliver_to_underage_student(*args, **kwargs)
        else:
            if 'deliver_to_student' in methods:
                return self.deliver_to_student(*args, **kwargs)

class WelcomeNotification(Notification):
    def __init__(self):
        super(WelcomeNotification, self).__init__('welcome')

    @classmethod
    def deliver(cls, *args, **kwargs):
        return cls().deliver_email(*args, **kwargs)

    def deliver_to_mentor(self, mentor):
        return self.email_mentor([mentor.email], 'Welcome to the Curiosity Machine!', {'mentor': mentor})

    def deliver_to_student(self, student):
        return self.email_student([student.email], 'Welcome to Curiosity Machine!', {'student': student})

    def deliver_to_underage_student(self, student):
        return self.email_underage_student([student.email], 'Activate Your Child’s Curiosity Machine Account', {'student': student})

class ActivationConfirmationNotification(Notification): 

    def __init__(self):
        super(ActivationConfirmationNotification, self).__init__('activation_confirmation')

    @classmethod
    def deliver(cls, *args, **kwargs):
        return cls().deliver_email(*args, **kwargs)

    def deliver_to_underage_student(self, student):
        self.email_underage_student([student.email], 'Your Child’s Curiosity Machine Account Is Now Active', {'student': student})

class InactiveNotification(Notification): 

    def __init__(self):
        super(InactiveNotification, self).__init__('inactive')

    @classmethod
    def deliver(cls, *args, **kwargs):
        return cls().deliver_email(*args, **kwargs)
    
    def deliver_to_student(self, student):
        return self.email_student([student.email], 'Start Inventing with Curiosity Machine!', {'student': student})

    def deliver_to_underage_student(self, student):
        return self.email_underage_student([student.email], 'Start Inventing with Curiosity Machine!', {'student': student})

class FirstProjectNotification(Notification): 

    def __init__(self):
        super(FirstProjectNotification, self).__init__('first_project')

    @classmethod
    def deliver(cls, *args, **kwargs):
        return cls().deliver_email(*args, **kwargs)

    def deliver_to_student(self, student):
        return self.email_student([student.email], 'Success! Your Curiosity Machine Project Was Submitted', {'student': student})

    def deliver_to_underage_student(self, student):
        return self.email_underage_student([student.email], 'Success! Your Child’s Curiosity Machine Project Was Submitted', {'student': student})

class MentorRespondedNotification(Notification): 

    def __init__(self):
        super(MentorRespondedNotification, self).__init__('mentor_responded')

    @classmethod
    def deliver(cls, *args, **kwargs):
        return cls().deliver_email(*args, **kwargs)

    def deliver_to_student(self, student, progress, mentor):
        return self.email_student([student.email], 'A Curiosity Machine Mentor Responded to Your Project', {'student': student, 'mentor': mentor, 'progress': progress})

    def deliver_to_underage_student(self, student, mentor):
        return self.email_underage_student([student.email], 'A Curiosity Machine Mentor Responded to Your Child’s Project', {'student': student, 'mentor': mentor})

class ProjectCompletionNotification(Notification): 

    def __init__(self):
        super(ProjectCompletionNotification, self).__init__('project_completion')

    @classmethod
    def deliver(cls, *args, **kwargs):
        return cls().deliver_email(*args, **kwargs)

    def deliver_to_student(self, student, progress):
        return self.email_student([student.email], 'Publish Your Curiosity Machine Project', {'student': student, 'progress': progress, 'stage': "inspiration"})

    def deliver_to_underage_student(self, student, progress):
        return self.email_underage_student([student.email], 'Publish Your Child’s Curiosity Machine Project', {'student': student, 'progress': progress, 'stage': "inspiration"})

class PublishNotification(Notification): 

    def __init__(self):
        super(PublishNotification, self).__init__('publish')

    @classmethod
    def deliver(cls, *args, **kwargs):
        return cls().deliver_email(*args, **kwargs)

    def deliver_to_student(self, student, progress):
        return self.email_student([student.email], 'Thanks for Sharing Your Curiosity Machine Project!', {'student': student, 'progress': progress, 'stage': "inspiration"})

    def deliver_to_underage_student(self, student, progress):
        return self.email_underage_student([student.email], 'Thanks for Sharing on Curiosity Machine!', {'student': student, 'progress': progress, 'stage': "inspiration"})

class EncouragementNotification(Notification): 

    def __init__(self):
        super(EncouragementNotification, self).__init__('encouragement')

    @classmethod
    def deliver(cls, *args, **kwargs):
        return cls().deliver_email(*args, **kwargs)
    
    def deliver_to_mentor(self, mentor):
        return self.email_mentor([mentor.email], 'New Students Projects on Curiosity Machine!', {'mentor': mentor})


class StudentRespondedNotification(Notification): 

    def __init__(self):
        super(StudentRespondedNotification, self).__init__('student_responded')

    @classmethod
    def deliver(cls, *args, **kwargs):
        return cls().deliver_email(*args, **kwargs)
    
    def deliver_to_mentor(self, mentor, progress, student):
        return self.email_mentor([mentor.email], 'Your Student Responded!', {'mentor': mentor, 'student': student, 'progress': progress})

class StudentCompletedNotification(Notification): 

    def __init__(self):
        super(StudentCompletedNotification, self).__init__('student_completed')

    @classmethod
    def deliver(cls, *args, **kwargs):
        return cls().deliver_email(*args, **kwargs)
    
    def deliver_to_mentor(self, mentor):
        return self.email_mentor([mentor.email], 'Your Student Completed Their project!', {'mentor': mentor})

class ModuleCompletedNotification(Notification): 

    def __init__(self):
        super(StudentCompletedNotification, self).__init__('module_completed')

    @classmethod
    def deliver(cls, *args, **kwargs):
        return cls().deliver_email(*args, **kwargs)
    
    def deliver_to_mentor(self, mentor):
        return self.email_mentor([mentor.email], 'Get Started on Curiosity Machine!', {'mentor': mentor})


