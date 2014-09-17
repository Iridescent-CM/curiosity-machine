from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.template import Context, TemplateDoesNotExist
import os.path
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .tasks import deliver_email
import django_rq

CM_EMAILS_ROOT = os.path.abspath(os.path.dirname(__file__))

#check this out: http://code.activestate.com/recipes/473810-send-an-html-email-with-embedded-image-and-plain-t/
class EmailTemplate(object):
	def __init__(self, recipients, subject, template_name,context={}, sender=settings.DEFAULT_FROM_EMAIL, cc_recipients=None):
		ctx = {'site_url': settings.SITE_URL}
		ctx.update(context)
		self.context = Context(ctx, autoescape=False)
		self.sender = sender
		self.subject = subject
		self.template_name = template_name
		self.recipients = recipients
		self.cc_recipients = cc_recipients

	def render_body_content(self, content_type='html'):
		return render_to_string("%s.%s" % (self.template_name, content_type), self.context)

	def render_html_body(self):
		html_part = MIMEMultipart(_subtype='related')
		html_part.attach(MIMEText(self.render_body_content('html'),  _subtype='html'))
		
		embedded_image = open('/'.join([CM_EMAILS_ROOT, 'static', 'images', 'CM_banner.png']), 'rb')
		img = MIMEImage(embedded_image.read(), 'png')
		embedded_image.close()
		
		img.add_header('Content-Id', '<banner>')  # angle brackets are important
		img.add_header("Content-Disposition", "inline", filename="banner") 
		html_part.attach(img)
		return html_part
		

	def render_subject(self):
		return self.subject

	def render_recipients(self):
		return self.recipients

	def render_cc_recipients(self):
		return self.cc_recipients

	def deliver(self):
		subject, from_email, to = self.render_subject(), self.sender, self.recipients
		text_content = self.render_body_content()
		html_part = self.render_html_body()
		cc = self.render_cc_recipients()
		django_rq.enqueue(deliver_email, subject, from_email, to, text_content, html_part, cc)
		