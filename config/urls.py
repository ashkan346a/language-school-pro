"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from apps.core.views import home, about, pricing

urlpatterns = [
    path('admin/', admin.site.urls),

    # The stunning public experience
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('pricing/', pricing, name='pricing'),

    # Temporary redirects so LOGIN_URL / dashboard references don't 404 or reverse-crash
    # (full custom auth + dashboard pages are planned for next iteration)
    path('login/', RedirectView.as_view(url='/admin/login/', permanent=False), name='login'),
    path('dashboard/', RedirectView.as_view(url='/admin/', permanent=False), name='dashboard'),

    # TODO (next phases): courses, auth, dashboard, learning, enrollment, certificates
    # path('courses/', include('apps.catalog.urls')),
    # path('accounts/', include('django.contrib.auth.urls')),
    # path('dashboard/', ...),

    path('favicon.ico', RedirectView.as_view(url='/static/img/favicon.ico', permanent=True)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

