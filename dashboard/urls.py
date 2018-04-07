"""dashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from apple.views import index,customers,stream_api_post,profile,resolve_api_post,autoreply_api

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^customers', customers),
    url(r'streaming_api',stream_api_post),
    url(r'autoreply_api',autoreply_api),
    url(r'resolve_api',resolve_api_post),
    url(r'^profile', profile),
    url(r'^',  index)
]
