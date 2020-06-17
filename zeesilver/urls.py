"""zeesilver URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.conf import settings
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.contrib.flatpages import views
from django.contrib.sitemaps.views import sitemap
from common.sitemaps import StaticSiteMap
from listings.sitemaps import ListingSiteMap

sitemaps = {
    'listings': ListingSiteMap,
    'static': StaticSiteMap
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('baton/', include('baton.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('common.urls')),
    path('gallery/', include('listings.urls')),
    path('search/', include('search.urls')),
    path('contact/', include('contact.urls')),
    path('cart/', include('cart.urls')),
    path('merchant/', include('merchant.urls')),
    path('shop/', include('shop.urls')),
    path(
        'sitemap.xml', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'
    ),
]

urlpatterns += [
    path('about/', views.flatpage, {'url': '/about/'}, name='about'),
    path('policies/', views.flatpage, {'url': '/policies/'}, name='policies'),
    re_path(r'^(P?<url>.*/)$', views.flatpage)
]

admin.site.site_header = settings.ADMIN_SITE_HEADER
admin.site.site_title = settings.ADMIN_SITE_TITLE

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
