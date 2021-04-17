from django import forms
from betterforms.forms import Fieldset, BetterModelForm
from assistenten.models import SchichtTemplate
from assistenten.widgets import XDSoftTimePickerInput


class SchichtTemplatesForm(BetterModelForm):
    class Meta:
        fields = ['bezeichner', 'beginn', 'ende']
        model = SchichtTemplate

        fieldsets = (
            Fieldset('schicht_template', fields=(
                'bezeichner',
                'beginn',
                'ende'),
                legend='Schicht-Vorlage hinzufügen'),
        )

    bezeichner = forms.CharField(label='Bezeichner (z.B. Früh, Spät, Tag-Schicht)',
                                 max_length=100,
                                 required=False
                                 )
    beginn = forms.TimeField(
        input_formats=['%H:%M'],
        widget=XDSoftTimePickerInput(),
        required=False
    )
    ende = forms.TimeField(
        input_formats=['%H:%M'],
        widget=XDSoftTimePickerInput(),
        required=False
    )
