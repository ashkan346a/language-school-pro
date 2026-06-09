from django import template
from django.utils.safestring import mark_safe

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

@register.simple_tag
def space_icon(key, color="#00e5ff", size=22):
    """
    Unique miniature extraterrestrial space SVG icons. Non-generic, bespoke for Aether.
    Keys: planet, constellation, rocket, satellite, telemetry, binary, trajectory, nebula, glyph, hud, comet, station, etc.
    Usage: {% space_icon "constellation" "#7c3aed" 18 %}
    """
    k = (key or "planet").lower()
    c = color or "#00e5ff"
    s = size or 22
    svg = '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.55" stroke-linecap="round" stroke-linejoin="round" class="mini-space-icon" style="color:{c}"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/></svg>'

    if k in ("planet", "ringed-planet"):
        svg = '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.6"><circle cx="12" cy="12" r="5"/><ellipse cx="12" cy="12" rx="9" ry="3.1" transform="rotate(-18 12 12)"/></svg>'
    elif k == "constellation":
        svg = '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.65"><circle cx="5" cy="5" r="1.6"/><circle cx="19" cy="7" r="1.6"/><circle cx="9" cy="18" r="1.6"/><circle cx="17" cy="17" r="1.6"/><path d="M6 6l12 10"/></svg>'
    elif k == "rocket":
        svg = '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.55"><path d="M12 3l7 7-7 11-7-11 7-7z"/><path d="M12 21v-3"/><circle cx="9" cy="10" r="1"/><circle cx="15" cy="10" r="1"/></svg>'
    elif k == "satellite":
        svg = '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.5"><rect x="8" y="8" width="8" height="8" rx="1"/><path d="M4 12h3M17 12h3M12 4v3M12 17v3"/><circle cx="12" cy="12" r="1.6"/></svg>'
    elif k in ("telemetry", "signal"):
        svg = '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.6"><path d="M4 14l4-4 4 4 8-8"/><path d="M18 6v4M18 6h-4"/></svg>'
    elif k in ("binary", "glyph"):
        svg = '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.5"><circle cx="7" cy="7" r="2"/><circle cx="17" cy="7" r="2"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/><path d="M9 7h6M9 17h6"/></svg>'
    elif k in ("trajectory", "arc"):
        svg = '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.55"><path d="M4 18c3.5-4 6-4 8-4s4.5 0 8 4"/><circle cx="12" cy="11" r="2.2"/><circle cx="5.5" cy="18.5" r="1"/><circle cx="18.5" cy="18.5" r="1"/></svg>'
    elif k in ("nebula", "cluster"):
        svg = '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.4"><circle cx="8" cy="9" r="2.8" opacity="0.7"/><circle cx="15" cy="8" r="2.2" opacity="0.55"/><circle cx="11" cy="15" r="3" opacity="0.65"/><path d="M6 14c2 1.5 4 1 6 1.5"/></svg>'
    elif k in ("hud", "panel"):
        svg = '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.5"><rect x="5" y="5" width="14" height="14" rx="1.5"/><path d="M8 9h8M8 12h5M8 15h3"/></svg>'
    elif k == "comet":
        svg = '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.5"><circle cx="7" cy="7" r="2"/><path d="M9 9l9 9M15 6l3-3M18 9l3 3"/></svg>'
    elif k in ("station", "orbital"):
        svg = '<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.5"><circle cx="12" cy="12" r="3"/><path d="M12 3v4M12 17v4M3 12h4M17 12h4"/><circle cx="12" cy="12" r="6.5" opacity="0.35"/></svg>'

    svg = svg.format(s=s, c=c)
    return mark_safe(svg)
