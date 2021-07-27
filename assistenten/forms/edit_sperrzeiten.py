from betterforms.forms import BetterModelForm, Fieldset
from django import forms
from assistenten.models import Sperrzeit, FesteSperrzeit
from assistenten.widgets import XDSoftDateTimePickerInput, XDSoftTimePickerInput


class EditSperrzeitForm(BetterModelForm):
    class Meta:
        fields = ['beginn', 'ende']
        model = Sperrzeit

    beginn = forms.DateTimeField(
        input_formats=('%d.%m.%Y %H:%M', '%d.%m.%Y %H:%M:%S',),
        widget=XDSoftDateTimePickerInput(attrs={'autocomplete': 'off'}),
        # initial=datetime.now().strftime('%d.%m.%Y %H:%M')
    )
    ende = forms.DateTimeField(
        input_formats=('%d.%m.%Y %H:%M', '%d.%m.%Y %H:%M:%S',),
        widget=XDSoftDateTimePickerInput(attrs={'autocomplete': 'off'}),
        # initial=datetime.now().strftime('%d.%m.%Y %H:%M')
    )


class FesteSperrzeitForm(BetterModelForm):
    class Meta:
        fields = ['wochentag', 'beginn', 'ende']
        model = FesteSperrzeit

    CHOICES = [
        ('-1', 'keine neue regelmäßige Sperrzeit'),
        ('1', 'Montag'),
        ('2', 'Dienstag'),
        ('3', 'Mittwoch'),
        ('4', 'Donnerstag'),
        ('5', 'Freitag'),
        ('6', 'Samstag'),
        ('7', 'Sonntag')]
    wochentag = forms.CharField(label='Wochentag', widget=forms.Select(choices=CHOICES))
    beginn = forms.TimeField(
        input_formats=['%H:%M'],
        widget=XDSoftTimePickerInput(attrs={'autocomplete': 'off'}),
        required=False
    )
    ende = forms.TimeField(
        input_formats=['%H:%M'],
        widget=XDSoftTimePickerInput(attrs={'autocomplete': 'off'}),
        required=False
    )
