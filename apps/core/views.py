from django.shortcuts import render
from django.http import HttpResponse
from .models import SiteSettings, Language, Stat, Feature, Testimonial, FAQ


def home(request):
    """Stunning public landing page."""
    settings = SiteSettings.load()
    languages = Language.objects.filter(is_active=True)
    stats = Stat.objects.filter(is_active=True)[:6]
    features = Feature.objects.filter(is_active=True)[:6]
    testimonials = Testimonial.objects.filter(is_featured=True)[:6]
    faqs = FAQ.objects.filter(is_active=True)[:8]

    context = {
        'site': settings,
        'languages': languages,
        'stats': stats,
        'features': features,
        'testimonials': testimonials,
        'faqs': faqs,
    }
    return render(request, 'public/home.html', context)


def about(request):
    return render(request, 'public/about.html', {'site': SiteSettings.load()})


def pricing(request):
    # Placeholder — can be expanded with editable pricing tiers later
    return render(request, 'public/pricing.html', {'site': SiteSettings.load()})
