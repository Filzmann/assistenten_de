from betterforms.forms import Fieldset
from django import forms
from betterforms.forms import Fieldset, BetterModelForm
from assistenten.models import FesteSchicht
from assistenten.widgets import XDSoftTimePickerInput


class SchichtTemplatesForm(BetterModelForm):
    class Meta:
        fields = ['beginn', 'ende']
        model = FesteSchicht

        fieldsets = (
            Fieldset('schicht_template', fields=(
                'bezeichner',
                'beginn',
                'ende'),
                legend='Schicht-Vorlage hinzufügen'),
        )

    bezeichner = forms.CharField(label='Bezeichner (z.B. Früh, Spät, Tag-Schicht)', max_length=100)

    beginn = forms.TimeField(
        input_formats=['%H:%M'],
        widget=XDSoftTimePickerInput()
    )
    ende = forms.TimeField(
        input_formats=['%H:%M'],
        widget=XDSoftTimePickerInput()
    )
