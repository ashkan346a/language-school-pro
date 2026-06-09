"""
Global context for Aether templates. Provides defensive site settings so
every page (including error pages or simple views) has the basics.
"""
from .models import SiteSettings


def site_settings(request):
    try:
        site = SiteSettings.load()
    except Exception:
        class _Dummy:
            site_name = "Aether"
            tagline = "Chart your course to fluency."
            meta_description = "Premium extraterrestrial language learning."
        site = _Dummy()
    return {'site': site}
