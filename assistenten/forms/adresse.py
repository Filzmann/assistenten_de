from django import forms
from assistenten.models import Adresse


class AddressForm(forms.ModelForm):
    class Meta:
        fields = ['bezeichner', 'strasse', 'hausnummer', 'plz', 'stadt']
        model = Adresse

    bezeichner = forms.CharField(label='Bezeichner', max_length=100)
    strasse = forms.CharField(label='Straße', max_length=100)
    hausnummer = forms.CharField(label="Hausnummer", max_length=5)
    plz = forms.CharField(label="PLZ", max_length=5)
    stadt = forms.CharField(label="Stadt", max_length=100)


class HomeForm(AddressForm):
    bezeichner = forms.CharField(widget=forms.HiddenInput(), initial='home', required=False)
