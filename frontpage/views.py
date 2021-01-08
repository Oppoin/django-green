from django.shortcuts import render
from django.views.generic.base import RedirectView


# Create your views here.
def index(request):
    return render(request, "index.html", context={})


from django.views.generic import TemplateView


class Home(TemplateView):
    template_name = "home.html"


class About(TemplateView):
    template_name = "core/about.html"


class LoginRedirectView(RedirectView):
    pattern_name = "redirect-to-login"

    def get_redirect_url(self, *args, **kwargs):
        return "/servers"
