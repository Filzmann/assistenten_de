from django import forms
from assistenten.models import ASN


class EditAsnStammdatenForm(forms.ModelForm):
    class Meta:
        fields = ['kuerzel', 'name', 'vorname', 'email', 'einsatzbuero']
        model = ASN

    kuerzel = forms.CharField(label='Kürzel', max_length=100)
    name = forms.CharField(label='Name', max_length=100)
    vorname = forms.CharField(label='Vorname', max_length=100)
    email = forms.EmailField(label="Email", max_length=100)

    CHOICES = [('1', 'Nordost'), ('2', 'West'), ('3', 'Süd')]
    einsatzbuero = forms.CharField(label='Einsatzbüro', widget=forms.Select(choices=CHOICES))

