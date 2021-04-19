from betterforms.forms import Fieldset, BetterModelForm
from django import forms
from django.http import request

from assistenten.models import ASN, EB, PFK, Adresse, Schicht
from assistenten.widgets import XDSoftDateTimePickerInput


class EditSchichtForm(BetterModelForm):
    class Meta:
        fields = [
            'beginn',
            'ende',
            'asn',
            'beginn_adresse',
            'ende_adresse',
            'ist_kurzfristig',
            'ist_ausfallgeld',
            'ist_assistententreffen',
            'ist_pcg',
            'ist_schulung']
        model = Schicht
        fieldsets = (
            Fieldset('wer', fields=('asn', ), legend='Bei Wem?'),
            Fieldset('zeit', fields=(
                'beginn',
                'ende',
                ), legend='Wann?'),
            Fieldset('ort', fields=(
                'beginn_adresse',
                'ende_adresse',
            ), legend='Wo?'),
            Fieldset('sonstiges', fields=(
                'ist_kurzfristig',
                'ist_ausfallgeld',
                'ist_assistententreffen',
                'ist_pcg',
                'ist_schulung'
            ), legend='Was?'),
        )

    asn = forms.ModelChoiceField(queryset=ASN.objects.all(), empty_label=None)

    beginn = forms.DateTimeField(
        input_formats=['%d.%m.%Y'],
        widget=XDSoftDateTimePickerInput()
    )
    ende = forms.DateTimeField(
        input_formats=['%d.%m.%Y'],
        widget=XDSoftDateTimePickerInput()
    )

    beginn_adresse = forms.ModelChoiceField(queryset=Adresse.objects.all(), empty_label=None)
    ende_adresse = forms.ModelChoiceField(queryset=Adresse.objects.all(), empty_label=None)

    ist_kurzfristig = forms.BooleanField()
    ist_ausfallgeld = forms.BooleanField()
    ist_assistententreffen = forms.BooleanField()
    ist_pcg = forms.BooleanField()
    ist_schulung = forms.BooleanField()
