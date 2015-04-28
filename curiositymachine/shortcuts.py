from django.shortcuts import get_object_or_404 as orig_get_object_or_404
from django.http import Http404, JsonResponse

def get_object_or_404(klass, format='html', *args, **kwargs):
	try:
		return orig_get_object_or_404(klass, *args, **kwargs)
	except Http404 as e:
		from .middleware import ViewException
		raise ViewException(format, str(e), 404)


def json_response(success, messages, fmt='html', **kwargs):
    if success:
        return JsonResponse(dict({'success': success, 'messages': messages}, **kwargs), content_type="application/json")
    else:
        return JsonResponse(dict({'success': success, 'errors': messages}, **kwargs), content_type="application/json")
