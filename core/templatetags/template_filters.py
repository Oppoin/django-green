from django import template

register = template.Library()


@register.filter(name="get_ip_address_from_do_droplet")
def get_ip_address_from_do_droplet(droplet):
    if "v4" in droplet.networks:
        networks = droplet.networks["v4"]
        for n in networks:
            if n["type"] == "public":
                return n["ip_address"]
    return "-"


@register.filter(name="get_attr_from_object")
def get_attr_from_object(object, attr):
    return getattr(object, attr)


@register.filter(name="get_display_from_size")
def get_display_from_size(size):
    # because we dont want to display 5.0 when 5 will do
    price_monthly = size.price_monthly
    if price_monthly.is_integer():
        price_monthly = int(price_monthly)

    # because we want to use gb instead of mb
    gigabyte = 1.0 / 1024
    memory_in_gb = gigabyte * size.memory

    return "{}GB RAM - {} CPU - {}GB SSD - ${} / Hour - ${} / Month".format(
        memory_in_gb, size.vcpus, size.disk, size.price_hourly, price_monthly
    )
