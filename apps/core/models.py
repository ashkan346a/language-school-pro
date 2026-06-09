from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class SiteSettings(models.Model):
    """Singleton-style global site configuration (editable in admin)."""
    site_name = models.CharField(max_length=100, default="Aether")
    tagline = models.CharField(max_length=200, default="Chart your course to fluency.")
    contact_email = models.EmailField(default="hello@aether.example")
    hero_title = models.CharField(max_length=200, default="Languages that take you to new worlds.")
    hero_subtitle = models.TextField(default="Join an extraordinary community of explorers mastering languages with a cosmic, premium experience. Every mission is designed to propel you forward.")
    hero_primary_cta = models.CharField(max_length=50, default="Begin Your Journey")
    hero_secondary_cta = models.CharField(max_length=50, default="Explore the Star Map")
    meta_description = models.CharField(max_length=160, default="Aether — Premium language learning with an extraterrestrial miniature space aesthetic. Stunning design, fully admin-configurable.")

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # Enforce singleton
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Language(models.Model):
    """Configurable languages for the constellation and courses."""
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=30, unique=True, blank=True)
    code = models.CharField(max_length=10, help_text="ISO code e.g. en, es, fr")
    accent_color = models.CharField(max_length=7, default="#00e5ff", help_text="Hex color for UI accents, e.g. #00e5ff")
    short_desc = models.CharField(max_length=160, blank=True)
    icon_key = models.CharField(max_length=40, default="planet", help_text="Key for custom SVG icon (planet, constellation, etc.)")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Language"
        verbose_name_plural = "Languages"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:30]
        super().save(*args, **kwargs)


class Stat(models.Model):
    """Homepage stats - fully configurable."""
    value = models.CharField(max_length=20)
    label = models.CharField(max_length=80)
    icon_key = models.CharField(max_length=40, default="rocket")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Stat"
        verbose_name_plural = "Stats"

    def __str__(self):
        return f"{self.value} {self.label}"


class Feature(models.Model):
    """Why Aether features with miniature custom icons."""
    icon_key = models.CharField(max_length=40, default="constellation")
    title = models.CharField(max_length=120)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Feature"
        verbose_name_plural = "Features"

    def __str__(self):
        return self.title


class Testimonial(models.Model):
    """Crew log style testimonials."""
    name = models.CharField(max_length=80)
    role = models.CharField(max_length=120, help_text="e.g. Mission Commander, Spanish • 420 light-years")
    quote = models.TextField()
    avatar = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    rating = models.PositiveSmallIntegerField(default=5)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"

    def __str__(self):
        return f"{self.name} — {self.role[:30]}"


class FAQ(models.Model):
    """Frequently asked questions, admin editable."""
    question = models.CharField(max_length=200)
    answer = models.TextField()
    category = models.CharField(max_length=50, default="General", blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question[:60]
