from django.http import QueryDict
from django import template
register = template.Library()

def qstring(**kwargs):
  ''' Create a query string from kwargs '''
  return '&'.join([k + '=' + str(v) for k, v in kwargs.items()])

def qstring_update(context, **kwargs):
  ''' Update/overwrite the current query string from kwargs '''
  request = context.get('request', None)
  if request is None:
    return ''
  qstring = request.GET.urlencode()
  qdict = QueryDict(qstring).copy()
  for k, v in kwargs.items():
    qdict[k] = v
  return qdict.urlencode()

register.simple_tag(qstring)
register.simple_tag(takes_context=True)(qstring_update)
