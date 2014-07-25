from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.template import Context, TemplateDoesNotExist
import os.path
from django.core.mail import EmailMessage
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.core.mail import EmailMessage


CM_EMAILS_ROOT = os.path.abspath(os.path.dirname(__file__))

templates_path = '../templates'
template_extensions = ('html', 'txt')


#check this out: http://code.activestate.com/recipes/473810-send-an-html-email-with-embedded-image-and-plain-t/
class EmailTemplate(object):
	def __init__(self, recipients, subject, template_name, context={}, sender=settings.DEFAULT_FROM_EMAIL):
		ctx = {'site_url': settings.SITE_URL}
		ctx.update(context)
		self.context = Context(ctx, autoescape=False)
		self.sender = sender
		self.subject = subject
		self.template_name = template_name
		self.recipients = recipients

	def render_body_content(self, type='txt'):
		try:
			return render_to_string("%s/%s.%s" % (templates_path, self.template_name, type), self.context)
		except Exception as e:
			print(str(e))
			return None

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

	def deliver(self):
		subject, from_email, to = self.render_subject(), self.sender, self.recipients
		text_content = self.render_body_content()
		html_part = self.render_html_body()
		msg = EmailMessage(subject, '', from_email, to)
		msg.attach(html_part)
		msg.send()
		