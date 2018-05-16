from django import template
register = template.Library()

def _slice(current, total, display_count):
    half = (display_count - 1) // 2
    last = min(total, max(display_count, current + half))
    first = max(1, last - display_count + 1)
    return range(first, last + 1)

@register.filter
def page_slice(page, display_count):
    """Takes a page and returns a slice of page_range of specified width"""
    current = page.number
    total = page.paginator.num_pages
    return _slice(current, total, display_count)

@register.simple_tag
def page_visibility_classes(page_num, active_page_num, total_pages):
    """Returns the appropriate bootstrap utility classes to show current page only
       for small widths and 5 items at medium width"""
    classes = "d-none"
    md_range = _slice(active_page_num, total_pages, 5)
    if page_num in md_range:
        classes += " d-md-block"
    elif page_num != active_page_num:
        classes += " d-lg-block"
    return classes

