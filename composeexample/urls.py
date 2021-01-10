"""composeexample URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from core.views import (
    ServerCreate,
    ServerDetail,
    ServerList,
    load_do_images,
    load_do_regions,
    load_do_sizes,
)
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path, re_path
from frontpage.views import About, Home, LoginRedirectView, LoginView  # new

urlpatterns = [
    # needed by allauth
    path("login/", LoginView.as_view(), name="login"),
    path("accounts/", include("allauth.urls")),
    # path("", include("frontpage.urls")),
    path("about", About.as_view(), name="about"),
    path("", LoginRedirectView.as_view(), name="redirect-to-login"),
    path("admin/", admin.site.urls),
    path("servers/create", ServerCreate.as_view(), name="servers-create"),
    path("servers/", ServerList.as_view(), name="servers-list"),
    path("servers/<int:pk>/delete", ServerDetail.as_view(), name="servers-detail"),
    path("do/sizes", load_do_sizes, name="load_do_sizes"),
    path("do/regions", load_do_regions, name="load_do_regions"),
    path("do/images", load_do_images, name="load_do_images"),
]
