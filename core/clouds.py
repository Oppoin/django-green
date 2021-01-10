import digitalocean
from allauth.socialaccount.models import SocialToken


class DigitalOceanCloud:
    def __init__(self, user):
        self.social_token = SocialToken.objects.filter(
            account__user=user, account__provider="digitalocean"
        ).first()

    def get_all_sizes(self):
        sizes = []
        if self.social_token:
            manager = digitalocean.Manager(token=self.social_token.token)
            sizes = manager.get_all_sizes()
        return sizes

    def get_all_regions(self):
        sizes = []
        if self.social_token:
            manager = digitalocean.Manager(token=self.social_token.token)
            sizes = manager.get_all_regions()
        return sizes

    def get_images(self, private=False, type=None):
        images = []
        if self.social_token:
            manager = digitalocean.Manager(token=self.social_token.token)
            images = manager.get_images(private=private, type=type)
        return images
