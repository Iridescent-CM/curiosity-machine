from django.conf import settings
from django.core.mail import EmailMessage

def deliver_email(subject, from_email, to, text_content, html_part):
	msg = EmailMessage(subject, '', from_email, to)
	msg.attach(html_part)
	msg.send()