from betterforms.forms import BetterModelForm
from django import forms
from assistenten.models import Urlaub
from assistenten.widgets import XDSoftDatePickerInput


class EditUrlaubForm(BetterModelForm):
    class Meta:
        fields = ['beginn', 'ende', 'status']
        model = Urlaub

    beginn = forms.DateField(
        input_formats=['%d.%m.%Y'],
        widget=XDSoftDatePickerInput(attrs={'autocomplete': 'off'})
    )
    ende = forms.DateField(
        input_formats=['%d.%m.%Y'],
        widget=XDSoftDatePickerInput(attrs={'autocomplete': 'off'})
    )

    CHOICES = [
        ('geplant', 'geplant'),
        ('beantragt', 'beantragt'),
        ('genehmigt', 'genehmigt'),

    ]
    status = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect())

