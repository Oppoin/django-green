from django import template

register = template.Library()


@register.filter(name="get_ip_address_from_do_droplet")
def get_ip_address_from_do_droplet(droplet):
    if "v4" in droplet.networks:
        return droplet.networks["v4"][0]["ip_address"]
    return "-"
