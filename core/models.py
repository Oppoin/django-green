from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    pass
    # add additional fields in here

    def __str__(self):
        return self.username


class Server(models.Model):
    name = models.CharField(max_length=200)
    provider_unique_fields = models.JSONField(default=dict)
