import digitalocean
from allauth.socialaccount.models import SocialToken
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured

# specific to ListView
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

# specific to ListView
from django.views.generic import ListView, View

# specific to CreateView
from django.views.generic.edit import CreateView, DeleteView

from core.clouds import DigitalOceanCloud
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
        context["is_empty"] = len(servers) == 0
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

    def get_context_data(self, **kwargs):
        docloud = DigitalOceanCloud(self.request.user)
        context = super().get_context_data(**kwargs)

        # provide the DO specific options such as sizes and the dependent regions
        sizes = context["sizes"] = docloud.get_all_sizes()
        first_size = sizes[0]
        regions = docloud.get_all_regions()
        first_region = regions[0]
        context["regions"] = [r for r in regions if r.slug in first_size.regions]
        images = docloud.get_images(type="distribution")
        filtered_images = [i for i in images if first_region.slug in i.regions]
        context["images"] = sorted(
            filtered_images, key=lambda x: (x.distribution, x.name), reverse=True
        )
        return context

    def form_valid(self, form):
        # to access the POSTed data use form.cleaned_data
        cleaned_data = form.cleaned_data

        social_token = SocialToken.objects.filter(
            account__user=self.request.user, account__provider="digitalocean"
        ).first()
        droplet = digitalocean.Droplet(
            token=social_token.token,
            name=cleaned_data["name"],
            region=cleaned_data["region"],  # New York 2
            image=cleaned_data["image"],  # Ubuntu 20.04 x64
            size_slug=cleaned_data["size"],  # 1GB RAM, 1 vCPU
            backups=False,
        )
        droplet.create()

        response = super().form_valid(form)

        if self.request.accepts("text/html"):
            return response


@method_decorator(login_required, name="dispatch")
class ServerDetail(DeleteView):
    # form_class = ServerCreateForm
    model = Server
    # template_name = "core/server/create.html"
    success_url = reverse_lazy("servers-list")

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        else:
            raise ImproperlyConfigured("No URL to redirect to. Provide a success_url.")

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        social_token = SocialToken.objects.filter(
            account__user=user, account__provider="digitalocean"
        ).first()

        droplet_id = kwargs["pk"]
        droplet = digitalocean.Droplet(id=droplet_id, token=social_token.token)

        droplet.destroy()

        success_url = self.get_success_url()

        return redirect(success_url)

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


def load_do_sizes(request):
    user = request.user
    social_token = SocialToken.objects.filter(
        account__user=user, account__provider="digitalocean"
    ).first()

    objects = []
    if social_token:
        manager = digitalocean.Manager(token=social_token.token)
        objects = manager.get_all_sizes()

    return render(request, "core/do/keys_as_options.html", {"objects": objects, "key": "slug"})


def load_do_regions(request):
    user = request.user
    social_token = SocialToken.objects.filter(
        account__user=user, account__provider="digitalocean"
    ).first()

    objects = []
    if social_token is None:
        return render(request, "core/do/regions.html", {"objects": objects})

    size_slug = request.GET.get("size", None)

    manager = digitalocean.Manager(token=social_token.token)
    regions = manager.get_all_regions()

    if size_slug is None:
        return render(request, "core/do/regions.html", {"objects": regions})

    sizes = manager.get_all_sizes()
    for size in sizes:
        if size.slug == size_slug:
            objects = [r for r in regions if r.slug in size.regions]
            break

    return render(request, "core/do/regions.html", {"objects": objects})


def load_do_images(request):
    user = request.user
    social_token = SocialToken.objects.filter(
        account__user=user, account__provider="digitalocean"
    ).first()

    objects = []
    if social_token is None:
        return render(request, "core/do/images.html", {"objects": objects})

    region_slug = request.GET.get("region", None)

    manager = digitalocean.Manager(token=social_token.token)
    distribution_images = manager.get_images(type="distribution")

    if region_slug is None:
        images = sorted(distribution_images, key=lambda x: (x.distribution, x.name), reverse=True)
        return render(request, "core/do/images.html", {"objects": images})

    filtered_images = [image for image in distribution_images if region_slug in image.regions]

    images = sorted(filtered_images, key=lambda x: (x.distribution, x.name), reverse=True)

    return render(request, "core/do/images.html", {"objects": images})
