from django.shortcuts import get_object_or_404 as orig_get_object_or_404
from django.http import Http404

def get_object_or_404(klass, format='html', *args, **kwargs):
	try:
		return orig_get_object_or_404(klass, *args, **kwargs)
	except Http404 as e:
		from .middleware import ViewException
		raise ViewException(format, str(e), 404)