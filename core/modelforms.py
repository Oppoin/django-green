from django import forms

from core.models import Server


class ServerCreateForm(forms.ModelForm):
    extra_field = forms.CharField(required=True)

    class Meta:
        model = Server
        fields = ("name", "extra_field")
