from django import forms
from assistenten.models import ASN


class FesteSchichtenForm(forms.ModelForm):
    class Meta:
        fields = ['wochentag', 'beginn', 'ende']
        model = ASN

    name = forms.CharField(label='Name', max_length=100)
    vorname = forms.CharField(label='Vorname', max_length=100)
    email = forms.EmailField(label="Email", max_length=100)

    CHOICES = [('0', 'Montag'),
               ('1', 'Dienstag'),
               ('2', 'Mittwoch'),
               ('3', 'Donnerstag'),
               ('4', 'Freitag'),
               ('5', 'Samstag'),
               ('6', 'Sonntag')]
    wochentag = forms.CharField(label='Wochentag', widget=forms.Select(choices=CHOICES))

