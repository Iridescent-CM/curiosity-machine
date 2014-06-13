from django.forms import widgets
from django.conf import settings

#JS_URL is the url to the filepicker.io javascript library
JS_VERSION = getattr(settings, "FILEPICKER_JS_VERSION", 1)
JS_URL = "//api.filepicker.io/v%d/filepicker.js" % (JS_VERSION)

class FilePickerInlineWidget(widgets.Input):
    input_type = "filepicker-custom"
    needs_multipart_form = False

    class Media:
        js = (JS_URL,)

class FilePickerDragDropWidget(widgets.Input):
    input_type = "filepicker-dragdrop"
    needs_multipart_form = False

    class Media:
        js = (JS_URL,)
