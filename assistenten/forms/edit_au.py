from betterforms.forms import BetterModelForm
from django import forms
from assistenten.models import AU
from assistenten.widgets import XDSoftDatePickerInput


class EditAUForm(BetterModelForm):
    class Meta:
        fields = ['beginn', 'ende']
        model = AU

    beginn = forms.DateField(
        input_formats=['%d.%m.%Y'],
        widget=XDSoftDatePickerInput(attrs={'autocomplete': 'off'})
    )
    ende = forms.DateField(
        input_formats=['%d.%m.%Y'],
        widget=XDSoftDatePickerInput(attrs={'autocomplete': 'off'})
    )



