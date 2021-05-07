from betterforms.forms import BetterModelForm
from django import forms
from django.utils.datetime_safe import datetime

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
        input_formats=('%d.%m.%Y %H:%M', '%d.%m.%Y %H:%M:%S',),
        widget=XDSoftDateTimePickerInput(),
        # initial=datetime.now().strftime('%d.%m.%Y %H:%M')
    )
    ende = forms.DateTimeField(
        input_formats=('%d.%m.%Y %H:%M', '%d.%m.%Y %H:%M:%S',),
        widget=XDSoftDateTimePickerInput(),
        # initial=datetime.now().strftime('%d.%m.%Y %H:%M')
    )

    beginn_adresse = forms.ModelChoiceField(queryset=Adresse.objects.filter(asn=None),
                                            empty_label='Neue Adresse eingeben',
                                            required=False
                                            )
    ende_adresse = forms.ModelChoiceField(queryset=Adresse.objects.filter(asn=None),
                                          empty_label='Neue Adresse eingeben',
                                          required=False
                                          )

    ist_kurzfristig = forms.BooleanField(label='BSD/RB', required=False)
    ist_ausfallgeld = forms.BooleanField(label='Ausfallgeld', required=False)
    ist_assistententreffen = forms.BooleanField(label='AT', required=False)
    ist_pcg = forms.BooleanField(label='PCG/PCS', required=False)
    ist_schulung = forms.BooleanField(label='Schulung', required=False)

    templates = forms.ModelChoiceField(queryset=None,
                                       required=False,
                                       empty_label=None,
                                       widget=forms.RadioSelect(attrs={"onClick": 'use_template()'}))

    def __init__(self, *args, **kwargs):
        """ entfernt den Doppelpunkt am Ende jedes Labels
            und schleust den request in die Form ein"""
        # TODO irgendwo eher den request schon aus der instance auspacken
        self.request = kwargs.pop('request')
        self.label_suffix = ""  # Removes : as label suffix

        super(EditSchichtForm, self).__init__(*args, **kwargs)

        self.fields['asn'].queryset = ASN.objects.filter(assistents__id=self.request.user.assistent.id)

        # wenn irgendwelche Daten schon in der instance sind, nehme ich die von da
        if kwargs['instance']:
            # werden seine Templates geladen
            self.fields['templates'].queryset = SchichtTemplate.objects.filter(
                asn__id=kwargs['instance'].asn.id)

            # und seine Adresslisten
            self.fields['beginn_adresse'].queryset = Adresse.objects.filter(asn__id=kwargs['instance'].asn.id)
            # damit fliegt das empty_label raus und muss neu rangehangen werden...
            self.fields['beginn_adresse'].empty_label = 'Neue Adresse eingeben'
            self.fields['ende_adresse'].queryset = Adresse.objects.filter(asn__id=kwargs['instance'].asn.id)
            self.fields['ende_adresse'].empty_label = 'Neue Adresse eingeben'

        # in der createView sind die Daten noch im Post-Array
        # sollte was im PostArray sein, wird überschrieben.
        # Daher muss zwingend erst instance und dann kwargs[data abgefragt werden.]
        if kwargs['data']:
            # und da zufällig ein asn für die Schicht ausgewählt ist
            if kwargs['data']['schicht-asn']:
                # werden seine Templates geladen
                self.fields['templates'].queryset = SchichtTemplate.objects.filter(
                    asn__id=kwargs['data']['schicht-asn'])

                # und seine Adresslisten
                self.fields['beginn_adresse'].queryset = Adresse.objects.filter(
                    asn__id=kwargs['data']['schicht-asn'])
                # damit fliegt das empty_label raus und muss neu rangehangen werden...
                self.fields['beginn_adresse'].empty_label = 'Neue Adresse eingeben'
                self.fields['ende_adresse'].queryset = Adresse.objects.filter(asn__id=kwargs['data']['schicht-asn'])
                self.fields['ende_adresse'].empty_label = 'Neue Adresse eingeben'
