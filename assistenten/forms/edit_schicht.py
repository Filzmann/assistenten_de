from betterforms.forms import Fieldset, BetterModelForm
from django import forms
from assistenten.models import ASN, Adresse, Schicht, SchichtTemplate
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

    templates = forms.ModelChoiceField(queryset=SchichtTemplate.objects.all(),
                                       empty_label=None,
                                       widget=forms.RadioSelect())

    # entfernt den Doppelpunkt am Ende jedes Labels
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.label_suffix = ""  # Removes : as label suffix
        print(self.fields['asn'])


