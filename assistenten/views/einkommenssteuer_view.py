from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.utils.datetime_safe import datetime
from django.views.generic import TemplateView

from assistenten.models import Schicht
from assistenten.views.schicht_tabelle_view import split_by_null_uhr, get_duration
from assistenten_de.settings import GOOGLE_API_KEY


class EinkommenssteuerView(LoginRequiredMixin, TemplateView):
    model = Schicht
    context_object_name = 'einkommenssteuer'
    template_name = 'assistenten/einkommenssteuer.html'
    act_year = timezone.now().year

    def get_context_data(self, **kwargs):
        startjahr = self.request.user.assistent.einstellungsdatum.year
        endjahr = self.act_year
        jahre = {jahr: str(jahr) for jahr in range(startjahr, endjahr + 1)}
        jahre[-1] = 'Jahr auswählen'
        context = super().get_context_data(**kwargs)
        context['jahre'] = jahre

        if 'jahreswaehler' in self.request.GET:
            if int(self.request.GET['jahreswaehler']) in range(1900, 2200):
                self.act_year =  int(self.request.GET['jahreswaehler'])
                context['selected_jahr'] = self.act_year
            else:
                self.act_year = timezone.now().year
                context['selected_jahr'] = -1
        else:
            self.act_year = timezone.now().year
            context['selected_jahr'] = -1

        context['wege'] = self.calculate_wege()
        return context


        # print(GOOGLE_API_KEY)
    def calculate_wege(self):
        # alle Schichten aus dem gewählten Jahr
        start=timezone.make_aware(datetime(year=self.act_year, month=1, day=1))
        end=timezone.make_aware(datetime(year=self.act_year+1,month=1,day=1))
        schichten = Schicht.objects.filter(
            beginn__range=(start, end)) | Schicht.objects.filter(
            ende__range=(start, end))

        # prüfen ob der hauptanteil der randschichten im aktuellen jahr liegt. wenn nicht fliegt die schicht aus der liste
        for schicht in schichten:
            if(schicht.beginn.year != schicht.ende.year):
                if self.get_schicht_hauptanteil(schicht).year != self.act_year:
                    print('muss raus')


    def get_schicht_hauptanteil(self, schicht):
        #TODO: Reisebegleitungen/mehrtägig
        teilschichten=split_by_null_uhr(schicht)
        maxschicht=None
        max_duration=0
        for teilschicht in teilschichten:
            dauer = get_duration(teilschicht['beginn'], teilschicht['ende'], 'hours')
            if dauer > max_duration:
                max_duration = dauer
                maxschicht = teilschicht
        return maxschicht['beginn']
