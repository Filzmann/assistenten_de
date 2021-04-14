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

    kuerzel = forms.CharField(label='Kürzel', max_length=100)
    name = forms.CharField(label='Name', max_length=100)
    vorname = forms.CharField(label='Vorname', max_length=100)
    email = forms.EmailField(label="Email", max_length=100)

    CHOICES = [('1', 'Nordost'), ('2', 'West'), ('3', 'Süd')]
    einsatzbuero = forms.CharField(label='Einsatzbüro', widget=forms.Select(choices=CHOICES))

    einsatzbegleitung = forms.ModelChoiceField(queryset=EB.objects.all(), empty_label=None)
    pflegefachkraft = forms.ModelChoiceField(queryset=PFK.objects.all(), empty_label=None)
