from django.shortcuts import render
from django.http import HttpResponse
from .models import SiteSettings, Language, Stat, Feature, Testimonial, FAQ


def _get_site_data():
    """
    Defensive loader for fresh deploys / before full migrate or empty DB.
    On Railway (especially first deploys or sqlite without volume), the tables
    may not exist yet when the first web request arrives.
    We return safe defaults so the beautiful landing page still renders.
    """
    try:
        site = SiteSettings.load()
    except Exception:
        # Table doesn't exist yet or other DB issue — provide minimal defaults
        class _Dummy:
            site_name = "Aether"
            tagline = "Chart your course to fluency."
            hero_title = "Languages that take you to new worlds."
            hero_subtitle = "An extraordinary platform for explorers. Configure everything from the admin after the first deploy."
            hero_primary_cta = "Begin Your Journey"
            hero_secondary_cta = "Explore the Star Map"
            meta_description = "Aether — Premium language learning with a stunning extraterrestrial design."
        site = _Dummy()

    try:
        languages = list(Language.objects.filter(is_active=True)[:7])
    except Exception:
        languages = []

    try:
        stats = list(Stat.objects.filter(is_active=True)[:6])
    except Exception:
        stats = []

    try:
        features = list(Feature.objects.filter(is_active=True)[:6])
    except Exception:
        features = []

    try:
        testimonials = list(Testimonial.objects.filter(is_featured=True)[:6])
    except Exception:
        testimonials = []

    try:
        faqs = list(FAQ.objects.filter(is_active=True)[:8])
    except Exception:
        faqs = []

    return site, languages, stats, features, testimonials, faqs


def home(request):
    """Stunning public landing page. Resilient on first deploy."""
    site, languages, stats, features, testimonials, faqs = _get_site_data()

    context = {
        'site': site,
        'languages': languages,
        'stats': stats,
        'features': features,
        'testimonials': testimonials,
        'faqs': faqs,
    }
    return render(request, 'public/home.html', context)


def about(request):
    site, _, _, _, _, _ = _get_site_data()
    return render(request, 'public/about.html', {'site': site})


def pricing(request):
    site, _, _, _, _, _ = _get_site_data()
    return render(request, 'public/pricing.html', {'site': site})
