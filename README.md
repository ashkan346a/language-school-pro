# Aether — Professional Extraterrestrial Language Learning Platform

Stunning, unique, miniature space-themed language education platform built with Django 5.1. Everything is **fully configurable from the Django admin** — hero copy, languages (European focus + English), courses with rich curriculum (modules + lessons), testimonials, features, stats, coupons, users, enrollments, certificates, and more.

Inspired by the clean, premium, distinctive aesthetic of Starlink and other high-end modern web experiences. No generic elements. Custom SVG icons, glassmorphism, holographic effects, orbital progress concepts, live canvas starfield, and "mission" language throughout.

## Key Features (MVP — Production Ready Foundation)

- **Public Experience**
  - Breathtaking hero with interactive starfield canvas + floating miniature elements
  - "The Constellation": interactive language nodes (English, Spanish, French, German, Italian, Portuguese, Russian)
  - Features, crew logs (testimonials), stats — all admin-editable
  - Course catalog foundation + detail-ready models

- **Admin Power**
  - Complete control over site content, courses (with inline modules/lessons), users/profiles, enrollments, certificates, coupons, transactions
  - Beautiful inlines and actions (e.g. bulk complete missions)

- **Student Journey**
  - Custom User + auto Student/Teacher profiles
  - Enrollment, LessonProgress, Assignments, Submissions, Certificates (PDF generation ready via ReportLab)
  - Progress recalculation

- **Payments**
  - Stripe keys wired in settings (test + live)
  - Coupon system (live validation ready for HTMX)
  - Manual admin fulfillment always available

- **Deployment**
  - Railway-ready (Procfile, runtime.txt, whitenoise, env-driven settings, collectstatic on release)
  - SQLite for now (per request) — trivial to switch to Postgres via `DATABASE_URL`

## Quick Local Start (Windows PowerShell)

```powershell
# 1. Create & activate venv (or use the one already at .venv)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install
pip install -r requirements.txt

# 3. Migrate + seed (magical demo data)
python manage.py migrate
python manage.py seed_aether

# 4. Superuser (or use the seeded one)
# admin@aether.example / aether2026!

# 5. Run
python manage.py runserver
```

Visit http://127.0.0.1:8000 — the home should feel special immediately.

Admin: http://127.0.0.1:8000/admin/

## Seeded Demo Data Highlights
- 7 Languages (European focus + English) with unique accent colors
- 4 rich Courses with Modules + Lessons (curriculum)
- Stats, Features (with custom miniature icons), Testimonials, FAQs, Coupons
- Superuser ready for instant exploration

Edit anything in the admin and refresh — the public site updates live.

## Design System (Unique & Non-Generic)
- Palette: deep space #05070f, glass #0f1429, cyan orbit #00e5ff, nebula violet #7c3aed, comet rose #ff4d94
- Components: `.glass`, `.holo`, `.orbit-btn`, constellation cards, orbital progress concepts
- Effects: canvas starfield (click for comets), subtle thruster hovers, premium micro-animations
- Language: "Initiate Launch", "Waypoint Reached", "Trajectory", "Sector", "Mission Control", etc.
- Icons: bespoke inline SVGs (planet rings, 4-dot constellations, rocket trails, etc.)

## Railway Deployment (GitHub connected)

1. Push this repo to GitHub.
2. In Railway: New Project → Deploy from GitHub repo.
3. Add these environment variables (generate a strong SECRET_KEY):
   - `SECRET_KEY` (long random)
   - `DEBUG=False`
   - `ALLOWED_HOSTS=your-app.railway.app,*.railway.app`
   - `STRIPE_PUBLISHABLE_KEY=...`
   - `STRIPE_SECRET_KEY=...`
   - (Optional) `DATABASE_URL` for Postgres
4. (For media persistence) Add a volume at `/app/media` if you enable user uploads (avatars, thumbnails, certs, assignments).
5. Deploy. The release phase runs migrate + collectstatic.

The site will be live with the seeded demo. Change the hero text, add courses, etc. instantly from `/admin`.

## Environment Variables (see .env.example)
- SECRET_KEY, DEBUG, ALLOWED_HOSTS
- STRIPE_* keys
- DATABASE_URL (optional)

## Next Steps / Continuation Ideas
- Full course explore + detail pages with HTMX filters
- Student dashboard + immersive learn view (HTMX lesson complete, orbital progress SVGs)
- Stripe checkout flow + enrollment activation
- Beautiful certificate PDF generation + gallery
- Auth (login/register with the cosmic glass style)
- Teacher profiles public + more

Everything is structured for rapid, high-quality expansion while keeping the unique extraterrestrial miniature aesthetic.

Built with love for explorers who deserve better than ordinary platforms.

---

**Status**: Core foundation complete, stunning public landing + admin fully wired + rich seed data + Railway artifacts. Ready for you to connect to Railway and continue iterating.
