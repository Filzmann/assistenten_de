from betterforms.forms import BetterModelForm
from django import forms
from guardian.shortcuts import get_objects_for_user

from assistenten.functions.person_functions import get_address
from assistenten.models import Schicht, SchichtTemplate, Assistent
from assistenten.widgets import XDSoftDateTimePickerInput


class AsnEditSchichtForm(BetterModelForm):
    class Meta:
        fields = [
            'beginn',
            'ende',
            'assistent',
            'beginn_adresse',
            'ende_adresse',
            'ist_kurzfristig',
            'ist_ausfallgeld',
            'ist_assistententreffen',
            'ist_pcg',
            'ist_schulung']
        model = Schicht

    assistent = forms.ModelChoiceField(queryset=None,
                                       empty_label='Neuer Assistent',
                                       widget=forms.Select(attrs={"onChange": 'create_new_or_submit()'}),
                                       required=False)

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

    beginn_adresse = forms.ModelChoiceField(queryset=None)
    ende_adresse = forms.ModelChoiceField(queryset=None)

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
        if 'request' in kwargs:
            self.request = kwargs.pop('request')

        self.label_suffix = ""  # Removes : as label suffix

        super(AsnEditSchichtForm, self).__init__(*args, **kwargs)
        self.fields['assistent'].queryset = get_objects_for_user(
            self.request.user, 'view_assistent', klass=Assistent, accept_global_perms=True)
        print(self.fields['assistent'].queryset)
        # wenn irgendwelche Daten schon in der instance sind, nehme ich die von da
        if hasattr(self.request.user, 'assistenznehmer'):
            asn = self.request.user.assistenznehmer
        elif 'instance' in kwargs:
            asn = kwargs['instance'].asn

        # get ASN Templates & addresses
        self.fields['templates'].queryset = SchichtTemplate.objects.filter(asn__id=asn.id)

        # und seine Adresslisten
        asn_addresses = get_address(asn=asn)
        asn_home = get_address(asn=asn, is_home=True).first()
        self.fields['beginn_adresse'].queryset = asn_addresses
        self.fields['ende_adresse'].queryset = asn_addresses
