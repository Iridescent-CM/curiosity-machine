from django import template
from django.conf import settings
import cloudinary

register = template.Library()

# Replaces an image url with a cloudinary url that dynamically resizes and caches the image.
# This is nearly identical to the built-in cloudinary_url tag, except that it only handles bare
# urls and will catch the exception that is thrown when cloudinary is not configured properly,
# and pass the image url straight through (graceful fail) for ease of development.
@register.simple_tag
def resized(source, options_dict={}, **options):
    options = dict(options_dict, **options)
    options['type'] = 'fetch' # force to fetch, as we expect bald urls and aren't using Cloudinary image objects in our app so far
    # now, implement graceful fail if CLOUDINARY_URL is not set...
    # the right thing to do here is obviously EAFP -- try to return a Cloudinary URL and catch an exception for the fallback case
    # unfortunately, the pycloudinary library only throws bare Exception() instances and not a subclass, so it's impossible to do
    # this safely (see issue #32 on pycloudinary github).  Instead we'll have to resort to an if/else clause that checks to see if
    # cloudinary is configured.
    if cloudinary.config().cloud_name:
        return cloudinary.CloudinaryImage(source).build_url(**options)
    else:
        return source
