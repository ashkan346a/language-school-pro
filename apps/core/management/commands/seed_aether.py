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

from apps.core.models import SiteSettings, Language, Stat, Feature, Testimonial, FAQ, PricingTier, CrewMember
from apps.catalog.models import Course, Module, Lesson
from apps.accounts.models import TeacherProfile
from apps.payments.models import Coupon

User = get_user_model()


class Command(BaseCommand):
    help = "Seed Aether with beautiful demo data (languages, courses, testimonials, etc.)"

    def handle(self, *args, **options):
        self.stdout.write("Seeding Aether demo data...")

        # Site settings (singleton) — Professional Persian
        site = SiteSettings.load()
        site.site_name = "اتر"
        site.tagline = "آموزش ممتاز زبان"
        site.hero_title = "زبان‌هایی که شما را به جهان‌های جدید می‌برند"
        site.hero_subtitle = "آکادمی زبان اتر — دوره‌های حرفه‌ای با اساتید بومی، برنامه‌های دقیق و نتیجه واقعی برای اهداف تحصیلی و شغلی شما."
        site.hero_primary_cta = "شروع کنید"
        site.save()

        # Languages — Persian descriptions for a true Persian-first premium school
        languages_data = [
            ("انگلیسی", "en", "#00e5ff", "زبان فرماندهی جهانی اکتشاف. از مذاکرات بین‌المللی تا داستان‌سرایی مدرن."),
            ("اسپانیایی", "es", "#ff4d94", "مسیرهای گرم از میان فرهنگ لاتین. ریتم، شور و زندگی."),
            ("فرانسوی", "fr", "#7c3aed", "دقت و ظرافت در هر واج. زبان دیپلماسی و هنر."),
            ("آلمانی", "de", "#22c55e", "ساختار و عمق در سطح مهندسی. دقت و قدرت بیان."),
            ("ایتالیایی", "it", "#f59e0b", "بیان ملودیک و پرشور. زبان زیبایی و طراحی."),
            ("پرتغالی", "pt", "#3b82f6", "سفرهای وسیع و روح‌انگیز. از برزیل تا اروپا."),
            ("روسی", "ru", "#a78bfa", "کیهان ادبی غنی و استقامت. عمق واقعی در کلمات."),
        ]
        langs = {}
        for name, code, color, desc in languages_data:
            lang, _ = Language.objects.get_or_create(
                name=name,
                defaults={"code": code, "accent_color": color, "short_desc": desc, "is_active": True}
            )
            langs[name] = lang

        # Stats (Persian premium)
        stats = [
            ("۲.۴k", "کاوشگر در حال حاضر در مدار"),
            ("۴۷", "زبان پرتاب شده تا امروز"),
            ("۹۴٪", "نرخ موفقیت ماموریت"),
            ("۳۱۲", "گواهی صادر شده این فصل"),
            ("۱۸", "میانگین سال نوری پیشرفت"),
        ]
        for i, (val, label) in enumerate(stats):
            Stat.objects.get_or_create(value=val, label=label, defaults={"order": i, "icon_key": "rocket"})

        # Features (miniature unique, Persian)
        features = [
            ("constellation", "برنامه درسی صورت فلکی", "هر ماژول بخشی از یک نقشه زنده است. ایستگاه‌ها را کامل کنید و ببینید صورت فلکی شخصی‌تان روشن می‌شود."),
            ("rocket", "بردار شتاب‌یافته", "روش اختصاصی ما سال‌ها پیشرفت را در ماموریت‌های متمرکز و زیبا فشرده می‌کند."),
            ("planet", "ارب‌های زنده زبان", "با همراهان هوش مصنوعی و انسان‌های واقعی در محیط‌های شبیه‌سازی شده مینیاتوری که زنده به نظر می‌رسند تمرین کنید."),
            ("satellite", "شبکه رله جهانی", "گروه‌های زنده بی‌وقفه در مناطق زمانی مختلف با ضبط‌هایی که حضور را القا می‌کنند."),
        ]
        for i, (icon, title, desc) in enumerate(features):
            Feature.objects.get_or_create(title=title, defaults={"icon_key": icon, "description": desc, "order": i})

        # Testimonials (crew logs, Persian)
        testimonials = [
            ("کاپیتان الن ووس", "اسپانیایی • ۶۸۰ سال نوری", "اتر فقط به من اسپانیایی یاد نداد — طرز فکرم را بازنویسی کرد. طراحی و ریتم آن فرازمینی است.", 5, "اسپانیایی"),
            ("دکتر ملیک رینز", "فرانسوی • مرکز فرماندهی", "حرفه‌ای‌ترین تجربه آموزشی که تا به حال دیده‌ام. هر پیکسل عمدی به نظر می‌رسد.", 5, "فرانسوی"),
            ("سوفیا کووالنکو", "روسی • فضای عمیق", "بالاخره روح زبان را درک کردم. نمای پیشرفت صورت فلکی اعتیادآور است.", 5, "روسی"),
        ]
        for name, role, quote, rating, lang_name in testimonials:
            Testimonial.objects.get_or_create(name=name, defaults={
                "role": role, "quote": quote, "rating": rating,
                "language": langs.get(lang_name), "is_featured": True
            })

        # FAQs Persian
        faqs = [
            ("تا رسیدن به مدار مکالمه چقدر طول می‌کشد؟", "اکثر دانشجویان با ماموریت‌های متمرکز ۵ ساعت در هفته به سطح B1 محکم در ۶–۹ هفته می‌رسند. مسیر شما شخصی است."),
            ("گروه‌های زنده واقعاً زنده هستند؟", "بله. گروه‌های کوچک (حداکثر ۸ نفر) با مربیان معمار بومی. تمام جلسات برای لاگ شخصی شما ضبط می‌شوند."),
            ("می‌توانم وسط ماموریت زبان را عوض کنم؟", "کاملاً. صورت فلکی پیشرفت شما با شما در هر زبانی که ارائه می‌دهیم سفر می‌کند."),
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

        # Courses + Curriculum (rich Persian titles & content)
        course_data = [
            ("اسپانیایی — مدار پایدار", "اسپانیایی", "B1", "ریتم و روح اسپانیایی را از طریق ایستگاه‌های فرهنگی و رله‌های زنده مسلط شوید.", 189, 10),
            ("فرانسوی — پروتکل فرماندهی", "فرانسوی", "B2", "دقت، ظرافت و زیبایی. برای کسانی که می‌خواهند مانند کسی که به هر اتاقی تعلق دارد صحبت کنند.", 249, 12),
            ("روسی — فضای عمیق", "روسی", "A2", "استقامت و عمق ادبی بسازید. پاداش‌بخش‌ترین مسیری که ارائه می‌دهیم.", 219, 14),
            ("ایتالیایی — بردار ملودیک", "ایتالیایی", "A1", "ورودی عالی برای روح‌های موسیقایی. پیروزی‌های فوری و صداهای زیبا.", 149, 6),
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
                    "what_you_will_learn": ["به مکالمه مطمئن برسید", "۱۲۰۰+ عبارت پرتاثیر را درونی کنید", "فرهنگ را مانند محلی‌ها ناوبری کنید", "یک ماموریت Capstone کامل کنید"],
                }
            )
            if created or course.modules.count() == 0:
                # Create 3-4 modules with lessons
                for m_idx in range(1, 5):
                    mod = Module.objects.create(course=course, title=f"ماژول {m_idx}: ایستگاه {m_idx}", order=m_idx, description="بلوک اصلی انتقال.")
                    for l_idx in range(1, 5):
                        Lesson.objects.create(
                            module=mod,
                            title=f"انتقال {l_idx}",
                            order=l_idx,
                            content_type="text",
                            content=f"### محتوای درس زیبا برای {title} ماژول {m_idx} درس {l_idx}.\n\nاینجا جایی است که محتوای آموزشی غنی، منحصر به فرد و غیرعمومی زندگی می‌کند. طراحی اطراف آن یادگیری را مانند اکتشاف می‌کند.",
                            duration_min=random.randint(8, 22),
                            is_preview=(l_idx == 1),
                        )

        # Coupons
        Coupon.objects.get_or_create(code="LAUNCH24", defaults={"percent_off": 24, "max_uses": 200, "is_active": True})
        Coupon.objects.get_or_create(code="CREW10", defaults={"percent_off": 10, "max_uses": 500, "is_active": True})

        # Pricing Tiers (for Manifest page)
        tiers = [
            ("Self-Paced Vector", "Complete autonomy. Lifetime access to transmissions.", 149, "one-time", ["Full constellation curriculum", "Progress orbs & telemetry", "Community relay access", "Certificate on completion"], False, 1),
            ("Live Cohort — Command", "Small crew. 8 weeks. Real-time architects.", 289, "8 weeks", ["Everything in Self-Paced", "Live vector sessions (max 8)", "Session recordings in your log", "Priority mission support", "Capstone review"], True, 2),
            ("Private Command", "1:1 with Lead Architect. Bespoke trajectory.", 0, "contact", ["Custom curriculum design", "Unlimited private relays", "Direct telemetry channel", "Personalized certificate + debrief", "Post-mission consultation"], False, 3),
        ]
        for name, tag, price, period, feats, featd, ord_ in tiers:
            PricingTier.objects.get_or_create(
                name=name,
                defaults={
                    "tagline": tag,
                    "price": price,
                    "period": period,
                    "features": feats,
                    "is_featured": featd,
                    "order": ord_,
                    "cta_label": "Contact Command" if price == 0 else "Begin Mission",
                }
            )

        # Crew for About
        crew_data = [
            ("Liora Vale", "Lead Language Architect", "15 years charting fluency trajectories. French & Spanish specialist.", "Language is the final frontier.", "#00e5ff"),
            ("Captain Kael Soto", "Orbital Linguist", "Deep space Russian & German programs. Known for elegant waypoint design.", "Every accent is a new star.", "#ff4d94"),
            ("Dr. Mira Solari", "Telemetry & Culture", "Italian & Portuguese vectors. Makes culture feel like home port.", "Fluency is belonging.", "#7c3aed"),
        ]
        for nm, role, bio, qt, col in crew_data:
            CrewMember.objects.get_or_create(name=nm, defaults={"role": role, "bio": bio, "quote": qt, "accent_color": col})

        self.stdout.write(self.style.SUCCESS("Aether seed complete. Visit /admin to explore and customize everything."))
        self.stdout.write("Recommended: createsuperuser, then login and tweak hero text, add more courses, etc.")
