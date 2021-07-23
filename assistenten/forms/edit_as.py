from betterforms.forms import Fieldset, BetterModelForm
from django import forms
from assistenten.models import Assistent
from assistenten.widgets import XDSoftDatePickerInput


class AsnEditAsForm(BetterModelForm):
    class Meta:
        fields = ['name', 'vorname', 'email']
        model = Assistent
        fieldsets = (
            Fieldset('info', fields=('name',
                                     'vorname',
                                     'email'), legend='Stammdaten'),
        )

    name = forms.CharField(label='Name', max_length=100, required=False)
    vorname = forms.CharField(label='Vorname', max_length=100, required=False)
    email = forms.EmailField(label="Email", max_length=100, required=False)

    def __init__(self, *args, **kwargs):
        """ schleust den request in die Form ein"""
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(AsnEditAsForm, self).__init__(*args, **kwargs)


class EditAsForm(AsnEditAsForm):
    class Meta:
        fields = ['name', 'vorname', 'email', 'einstellungsdatum']
        model = Assistent
        fieldsets = (
            Fieldset('info', fields=('name',
                                     'vorname',
                                     'email',
                                     'einstellungsdatum'), legend='Stammdaten'),
        )

    einstellungsdatum = forms.DateTimeField(
        input_formats=['%d.%m.%Y'],
        widget=XDSoftDatePickerInput(attrs={'autocomplete': 'off'}),
        required=False
    )
