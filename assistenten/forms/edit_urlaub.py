from betterforms.forms import BetterModelForm
from django import forms
from django.utils import timezone
from django.utils.datetime_safe import datetime, time

from assistenten.models import Urlaub
from assistenten.widgets import XDSoftDatePickerInput


class EditUrlaubForm(BetterModelForm):
    class Meta:
        fields = ['beginn', 'ende', 'status']
        model = Urlaub

    beginn = forms.DateField(
        input_formats=['%d.%m.%Y'],
        widget=XDSoftDatePickerInput(attrs={'autocomplete': 'off'})
    )
    ende = forms.DateField(
        input_formats=['%d.%m.%Y'],
        widget=XDSoftDatePickerInput(attrs={'autocomplete': 'off'})
    )

    CHOICES = [
        ('geplant', 'geplant'),
        ('beantragt', 'beantragt'),
        ('genehmigt', 'genehmigt'),

    ]
    status = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect())

    def clean(self):
        cleaned_data = super().clean()

        cleaned_data['beginn'] = timezone.make_aware(datetime.combine(cleaned_data['beginn'], time(0, 0)))
        cleaned_data['ende'] = timezone.make_aware(datetime.combine(cleaned_data['beginn'], time(23, 59, 59)))

        return cleaned_data
