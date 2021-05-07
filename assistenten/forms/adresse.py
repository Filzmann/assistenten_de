from betterforms.forms import Fieldset, BetterModelForm
from django import forms
from assistenten.models import Adresse


class AddressForm(BetterModelForm):
    class Meta:
        fields = ['bezeichner', 'strasse', 'hausnummer', 'plz', 'stadt']
        model = Adresse
        fieldsets = (
            Fieldset('adresse', fields=('bezeichner',
                                        'strasse',
                                        'hausnummer',
                                        'plz',
                                        'stadt'), legend='Adresse'),
        )

    bezeichner = forms.CharField(label='Bezeichner', max_length=100)
    strasse = forms.CharField(label='Straße', max_length=100, required=False)
    hausnummer = forms.CharField(label="Hausnummer", max_length=5, required=False)
    plz = forms.CharField(label="PLZ", max_length=5, required=False)
    stadt = forms.CharField(label="Stadt", max_length=100, required=False)

    def __init__(self, *args, **kwargs):
        """ entfernt den Doppelpunkt am Ende jedes Labels
            und schleust den request in die Form ein"""
        # TODO irgendwo eher den request schon aus der instance auspacken
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        self.label_suffix = ""  # Removes : as label suffix
        super(AddressForm, self).__init__(*args, **kwargs)
        # print("adresse_form_unten")
        # print(kwargs)


class HomeForm(AddressForm):
    bezeichner = forms.CharField(widget=forms.HiddenInput(), initial='home', required=False)
