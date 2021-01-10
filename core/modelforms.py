from django import forms

from core.models import Server


class ServerCreateForm(forms.ModelForm):
    size = forms.CharField(required=True)
    region = forms.CharField(required=True)
    image = forms.CharField(required=True)

    class Meta:
        model = Server
        fields = ("name", "size", "region", "image")
