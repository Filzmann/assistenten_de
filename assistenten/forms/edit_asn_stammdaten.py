from django import forms
from assistenten.models import ASN


class EditAsForm(forms.ModelForm):
    class Meta:
        fields = ['name', 'vorname', 'email', 'einstellungsdatum']
        model = ASN

    name = forms.CharField(label='Name', max_length=100)
    vorname = forms.CharField(label='Vorname', max_length=100)
    email = forms.EmailField(label="Deine Email", max_length=100)


