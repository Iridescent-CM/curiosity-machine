from django.conf import settings
from django.core.mail import EmailMessage

def deliver_email(subject, from_email, to, text_content, html_part, cc=None):
	if cc:
		print(cc)
		msg = EmailMessage(subject, '', from_email, to, cc=cc)
	else:
		msg = EmailMessage(subject, '', from_email, to)
	msg.attach(html_part)
	msg.send()