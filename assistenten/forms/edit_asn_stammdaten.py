from django import forms
from assistenten.models import ASN, EB, PFK


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

    CHOICES = EB.objects.all().values_list('id', 'email')

    einsatzbegleitung = forms.CharField(label='EB', widget=forms.Select(choices=CHOICES))

    CHOICES = PFK.objects.all().values_list('id', 'email')
    pflegefachkraft = forms.CharField(label='PFK', widget=forms.Select(choices=CHOICES))
