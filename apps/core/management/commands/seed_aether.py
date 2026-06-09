"""
python manage.py seed_aether

Creates a rich, realistic demo dataset for Aether so the site looks stunning
and fully functional immediately after migrate + createsuperuser.
Languages focused on English + European set per user preference.
"""
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.core.models import SiteSettings, Language, Stat, Feature, Testimonial, FAQ
from apps.catalog.models import Course, Module, Lesson
from apps.accounts.models import TeacherProfile
from apps.payments.models import Coupon

User = get_user_model()


class Command(BaseCommand):
    help = "Seed Aether with beautiful demo data (languages, courses, testimonials, etc.)"

    def handle(self, *args, **options):
        self.stdout.write("Seeding Aether demo data...")

        # Site settings (singleton)
        site = SiteSettings.load()
        site.site_name = "Aether"
        site.tagline = "Chart your course to fluency."
        site.hero_title = "Languages that take you to new worlds."
        site.hero_subtitle = "An extraordinary platform for explorers. Every mission is meticulously designed with a miniature extraterrestrial aesthetic. Fully configurable from this admin."
        site.save()

        # Languages (European focus + English)
        languages_data = [
            ("English", "en", "#00e5ff", "The universal command language of exploration."),
            ("Spanish", "es", "#ff4d94", "Warm trajectories through Latin culture."),
            ("French", "fr", "#7c3aed", "Precision and elegance in every phoneme."),
            ("German", "de", "#22c55e", "Engineering-grade structure and depth."),
            ("Italian", "it", "#f59e0b", "Melodic and passionate expression."),
            ("Portuguese", "pt", "#3b82f6", "Expansive, soulful voyages."),
            ("Russian", "ru", "#a78bfa", "Rich literary cosmos and resilience."),
        ]
        langs = {}
        for name, code, color, desc in languages_data:
            lang, _ = Language.objects.get_or_create(
                name=name,
                defaults={"code": code, "accent_color": color, "short_desc": desc, "is_active": True}
            )
            langs[name] = lang

        # Stats
        stats = [
            ("2.4k", "Explorers currently in orbit"),
            ("47", "Languages launched to date"),
            ("94%", "Mission success rate"),
            ("312", "Certificates minted this quarter"),
            ("18", "Average light-years progressed"),
        ]
        for i, (val, label) in enumerate(stats):
            Stat.objects.get_or_create(value=val, label=label, defaults={"order": i, "icon_key": "rocket"})

        # Features (miniature unique)
        features = [
            ("constellation", "Constellation Curriculum", "Every module forms part of a living map. Complete waypoints and watch your personal constellation light up."),
            ("rocket", "Accelerated Vector", "Our proprietary method compresses years of progress into focused, beautiful missions."),
            ("planet", "Living Language Orbs", "Practice with AI companions and real humans in miniature simulated environments that feel alive."),
            ("satellite", "Global Relay Network", "Seamless live cohorts across time zones with recordings that feel present."),
        ]
        for i, (icon, title, desc) in enumerate(features):
            Feature.objects.get_or_create(title=title, defaults={"icon_key": icon, "description": desc, "order": i})

        # Testimonials (crew logs)
        testimonials = [
            ("Captain Elena Voss", "Spanish • 680 light-years", "Aether didn’t just teach me Spanish — it rewired how I think. The design and pacing are otherworldly.", 5, "Spanish"),
            ("Dr. Malik Raines", "French • Mission Control", "The most premium educational experience I have ever encountered. Every pixel feels intentional.", 5, "French"),
            ("Sofia Kovalenko", "Russian • Deep Space", "I finally understand the soul of the language. The constellation progress view is addictive.", 5, "Russian"),
        ]
        for name, role, quote, rating, lang_name in testimonials:
            Testimonial.objects.get_or_create(name=name, defaults={
                "role": role, "quote": quote, "rating": rating,
                "language": langs.get(lang_name), "is_featured": True
            })

        # FAQs
        faqs = [
            ("How long until I reach conversational orbit?", "Most students achieve solid B1 in 6–9 weeks with focused 5h/week missions. Your trajectory is personal."),
            ("Are the live cohorts actually live?", "Yes. Small groups (max 8) with native architect instructors. All sessions recorded for your personal log."),
            ("Can I switch languages mid-mission?", "Absolutely. Your progress constellation travels with you across any language we offer."),
        ]
        for i, (q, a) in enumerate(faqs):
            FAQ.objects.get_or_create(question=q, defaults={"answer": a, "order": i})

        # Teachers (for courses)
        teacher_user, _ = User.objects.get_or_create(
            email="architect@aether.example",
            defaults={"username": "lead_architect", "first_name": "Liora", "last_name": "Vale", "is_staff": True}
        )
        teacher, _ = TeacherProfile.objects.get_or_create(
            user=teacher_user,
            defaults={"title": "Lead Language Architect", "bio": "15 years charting fluency trajectories across 9 languages.", "years_experience": 15, "short_quote": "Language is the final frontier."}
        )
        teacher.languages_taught.set([langs["French"], langs["Spanish"], langs["English"]])

        # Courses + Curriculum (rich)
        course_data = [
            ("Spanish — Stable Orbit", "Spanish", "B1", "Master the rhythm and soul of Spanish through cultural waypoints and live relays.", 189, 10),
            ("French — Command Protocol", "French", "B2", "Precision, nuance, and elegance. For those who want to speak like they belong in any room.", 249, 12),
            ("Russian — Deep Space", "Russian", "A2", "Build resilience and literary depth. The most rewarding trajectory we offer.", 219, 14),
            ("Italian — Melodic Vector", "Italian", "A1", "Perfect entry for musical souls. Immediate wins and beautiful sounds.", 149, 6),
        ]

        for title, lang_name, level, desc, price, weeks in course_data:
            course, created = Course.objects.get_or_create(
                title=title,
                defaults={
                    "language": langs[lang_name],
                    "level": level,
                    "description": desc,
                    "price": Decimal(price),
                    "duration_weeks": weeks,
                    "is_featured": True,
                    "instructor": teacher,
                    "what_you_will_learn": ["Reach confident conversation", "Internalize 1200+ high-impact phrases", "Navigate culture like a local", "Complete a capstone mission"],
                }
            )
            if created or course.modules.count() == 0:
                # Create 3-4 modules with lessons
                for m_idx in range(1, 5):
                    mod = Module.objects.create(course=course, title=f"Module {m_idx}: Waypoint {m_idx}", order=m_idx, description="Core transmission block.")
                    for l_idx in range(1, 5):
                        Lesson.objects.create(
                            module=mod,
                            title=f"Transmission {l_idx}",
                            order=l_idx,
                            content_type="text",
                            content=f"### Beautifully written lesson content for {title} module {m_idx} lesson {l_idx}.\n\nThis is where rich, unique, non-generic educational material lives. The design around it makes learning feel like exploration.",
                            duration_min=random.randint(8, 22),
                            is_preview=(l_idx == 1),
                        )

        # Coupons
        Coupon.objects.get_or_create(code="LAUNCH24", defaults={"percent_off": 24, "max_uses": 200, "is_active": True})
        Coupon.objects.get_or_create(code="CREW10", defaults={"percent_off": 10, "max_uses": 500, "is_active": True})

        self.stdout.write(self.style.SUCCESS("Aether seed complete. Visit /admin to explore and customize everything."))
        self.stdout.write("Recommended: createsuperuser, then login and tweak hero text, add more courses, etc.")
