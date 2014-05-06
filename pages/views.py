from django.shortcuts import render, get_object_or_404
from .models import Page

def static_page(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    return render(request, 'static_page.html', {'page': page})
