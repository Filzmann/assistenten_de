from betterforms.forms import Fieldset, BetterModelForm
from django import forms
from assistenten.models import ASN, Adresse, Schicht
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
            Fieldset('wer', fields=('asn',), legend='Bei Wem?'),
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

    asn = forms.ModelChoiceField(queryset=ASN.objects.all(),
                                 empty_label='Neuer ASN',
                                 widget=forms.Select(attrs={"onChange": 'submit()'}))

    beginn = forms.DateTimeField(
        input_formats=['%d.%m.%Y'],
        widget=XDSoftDateTimePickerInput()
    )
    ende = forms.DateTimeField(
        input_formats=['%d.%m.%Y'],
        widget=XDSoftDateTimePickerInput()
    )

    beginn_adresse = forms.ModelChoiceField(queryset=Adresse.objects.all(), empty_label="Zu Hause")
    ende_adresse = forms.ModelChoiceField(queryset=Adresse.objects.all(), empty_label="Zu Hause")

    ist_kurzfristig = forms.BooleanField(label='BSD/RB', required=False)
    ist_ausfallgeld = forms.BooleanField(label='Ausfallgeld', required=False)
    ist_assistententreffen = forms.BooleanField(label='AT', required=False)
    ist_pcg = forms.BooleanField(label='PCG/PCS', required=False)
    ist_schulung = forms.BooleanField(label='Schulung', required=False)

    # entfernt den Doppelpunkt am Ende jedes Labels
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""  # Removes : as label suffix
