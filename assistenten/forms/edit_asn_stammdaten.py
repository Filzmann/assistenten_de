from betterforms.forms import Fieldset, BetterModelForm
from django import forms
from assistenten.models import ASN, EB, PFK


class EditAsnStammdatenForm(BetterModelForm):
    class Meta:
        fields = [
            'kuerzel',
            'name',
            'vorname',
            'email',
            'einsatzbuero',
            'pflegefachkraft',
            'einsatzbegleitung']
        model = ASN
        fieldsets = (
            Fieldset('info', fields=(
                'kuerzel',
                'name',
                'vorname',
                'email'), legend='Stammdaten'),
            Fieldset('verbindungen', fields=(
                'einsatzbuero',
                'einsatzbegleitung',
                'pflegefachkraft'), legend='Zuordnung'),
        )

    kuerzel = forms.CharField(label='Kürzel', max_length=100, required=False,)
    name = forms.CharField(label='Name', max_length=100, required=False,)
    vorname = forms.CharField(label='Vorname', max_length=100, required=False,)
    email = forms.EmailField(label="Email", max_length=100, required=False,)

    CHOICES = [('1', 'Nordost'), ('2', 'West'), ('3', 'Süd')]
    einsatzbuero = forms.CharField(label='Einsatzbüro', widget=forms.Select(choices=CHOICES), required=False,)

    einsatzbegleitung = forms.ModelChoiceField(queryset=EB.objects.all(), empty_label=None, required=False,)
    pflegefachkraft = forms.ModelChoiceField(queryset=PFK.objects.all(), empty_label=None, required=False,)

    def __init__(self, *args, **kwargs):
        """ entfernt den Doppelpunkt am Ende jedes Labels
            und schleust den request in die Form ein"""
        # TODO irgendwo eher den request schon aus der instance auspacken
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        self.label_suffix = ""  # Removes : as label suffix
        super(EditAsnStammdatenForm, self).__init__(*args, **kwargs)
        # print("asn_form_unten")
        # print(kwargs)
