from django import forms
from assistenten.models import Assistent
from assistenten.widgets import XDSoftDatePickerInput


class EditAsForm(forms.ModelForm):
    class Meta:
        fields = ['name', 'vorname', 'email', 'einstellungsdatum']
        model = Assistent

    name = forms.CharField(label='Name', max_length=100)
    vorname = forms.CharField(label='Vorname', max_length=100)
    email = forms.EmailField(label="Deine Email", max_length=100)
    einstellungsdatum = forms.DateField(
        input_formats=['%d.%m.%Y'],
        widget=XDSoftDatePickerInput()
    )

