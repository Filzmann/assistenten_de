from django import forms
from betterforms.forms import Fieldset, BetterModelForm
from assistenten.models import FesteSchicht
from assistenten.widgets import XDSoftTimePickerInput


class FesteSchichtenForm(BetterModelForm):
    class Meta:
        fields = ['wochentag', 'beginn', 'ende']
        model = FesteSchicht
        liste = ['auauauaua', 2, 3]
        fieldsets = (
            Fieldset('feste_schicht', fields=('wochentag',
                                              'beginn',
                                              'ende'),
                     legend='Feste Schicht hinzufügen',
                     template_name="assistenten/fieldset_feste_schichten.html",
                     liste=liste),
        )

    CHOICES = [
        ('-1', 'keine neue feste Schicht'),
        ('0', 'Montag'),
        ('1', 'Dienstag'),
        ('2', 'Mittwoch'),
        ('3', 'Donnerstag'),
        ('4', 'Freitag'),
        ('5', 'Samstag'),
        ('6', 'Sonntag')]
    wochentag = forms.CharField(label='Wochentag', widget=forms.Select(choices=CHOICES))
    beginn = forms.TimeField(
        input_formats=['%H:%M'],
        widget=XDSoftTimePickerInput(),
        required=False
    )
    ende = forms.TimeField(
        input_formats=['%H:%M'],
        widget=XDSoftTimePickerInput(attrs={'autocomplete': 'off'}),
        required=False
    )
