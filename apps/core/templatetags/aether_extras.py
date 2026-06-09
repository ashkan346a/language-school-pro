from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Safe dict get for templates: {{ mydict|get_item:key }}"""
    if dictionary is None:
        return None
    try:
        return dictionary.get(key)
    except (AttributeError, TypeError):
        return None

@register.filter
def markdown(text):
    """Very basic markdown to HTML (headings, paragraphs, lists). For richer use bleach + markdown in view."""
    if not text:
        return ""
    import re
    text = re.sub(r'^### (.*)$', r'<h3 class="font-semibold text-lg mt-4 mb-1">\1</h3>', text, flags=re.M)
    text = re.sub(r'^## (.*)$', r'<h2 class="font-semibold text-xl mt-5 mb-2">\1</h2>', text, flags=re.M)
    text = re.sub(r'\n\n', '</p><p class="mt-3">', text)
    text = '<p>' + text.replace('\n', '<br>') + '</p>'
    return text
