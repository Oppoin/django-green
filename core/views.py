import digitalocean
from allauth.socialaccount.models import SocialToken
from django.contrib.auth.decorators import login_required

# specific to ListView
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

# specific to ListView
from django.views.generic import ListView

# specific to CreateView
from django.views.generic.edit import CreateView

from core.modelforms import ServerCreateForm
from core.models import Server


@method_decorator(login_required, name="dispatch")
class ServerList(ListView):
    model = Server
    template_name = "core/server/list.html"
    context_object_name = "servers"
    paginate_by = 100

    # SocialToken.objects.filter(account__user=user, account__provider='facebook')

    def get_queryset(self):
        user = self.request.user
        social_token = SocialToken.objects.filter(
            account__user=user, account__provider="digitalocean"
        ).first()

        if social_token:
            manager = digitalocean.Manager(token=social_token.token)
            default_project = manager.get_default_project()
            # see some writeup that explains why we use default project name as account name
            # TLDR DO APIv2 does not provide account name +
            # DO by default will create a default project with the same name as account name
            account_name = default_project.name
            return manager.get_all_droplets()

        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super(ServerList, self).get_context_data(**kwargs)

        servers = self.get_queryset()

        page = self.request.GET.get("page")
        paginator = Paginator(servers, self.paginate_by)
        try:
            servers = paginator.page(page)
        except PageNotAnInteger:
            servers = paginator.page(1)
        except EmptyPage:
            servers = paginator.page(paginator.num_pages)
        context["servers"] = servers
        return context


@method_decorator(login_required, name="dispatch")
class ServerCreate(CreateView):
    form_class = ServerCreateForm
    model = Server
    template_name = "core/server/create.html"
    # if set fields here they must be fields of model class
    # fields = ("name", "size")
    # if want to do something special best to use form class
    success_url = reverse_lazy("servers-list")

    def form_valid(self, form):
        # to access the POSTed data use form.cleaned_data
        cleaned_data = form.cleaned_data
        response = super().form_valid(form)
        if self.request.accepts("text/html"):
            return response


def load_do_sizes(request):
    user = request.user
    social_token = SocialToken.objects.filter(
        account__user=user, account__provider="digitalocean"
    ).first()

    sizes = []
    if social_token:
        manager = digitalocean.Manager(token=social_token.token)
        sizes = manager.get_all_sizes()

    return render(request, "core/do/sizes.html", {"sizes": sizes})
