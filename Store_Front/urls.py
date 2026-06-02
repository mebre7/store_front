from django.conf import settings
from django.urls import include, path
"""
URL configuration for Store_Front project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
admin.site.site_header = 'Storefront Admin'
admin.site.site_title = 'Storefront Admin Portal'
admin.site.index_title = 'Admin'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('playground/', include('playground.urls')),
    path('api/store/', include('store.urls')),
    path('store/', include('store.urls')),
]

if settings.DEBUG and 'debug_toolbar' in settings.INSTALLED_APPS:
    urlpatterns.append(path('__debug__/', include('debug_toolbar.urls')))
