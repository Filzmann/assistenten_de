import googlemaps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView

from assistenten.models import Schicht, Adresse, Weg
from assistenten.views.schicht_tabelle_view import split_by_null_uhr, get_duration
from assistenten_de.settings import GOOGLE_API_KEY


def get_schicht_hauptanteil(schicht):
    # TODO: Reisebegleitungen/mehrtägig
    teilschichten = split_by_null_uhr(schicht)
    maxschicht = None
    max_duration = 0
    for teilschicht in teilschichten:
        dauer = get_duration(teilschicht['beginn'], teilschicht['ende'], 'hours')
        if dauer > max_duration:
            max_duration = dauer
            maxschicht = teilschicht
    return maxschicht['beginn']


def make_weg(adresse1, adresse2):
    gmaps = googlemaps.Client(key=GOOGLE_API_KEY)
    adresse1_string = \
        adresse1.strasse + ' ' \
        + adresse1.hausnummer + ', ' \
        + adresse1.plz + ' ' \
        + adresse1.stadt

    adresse2_string = \
        adresse2.strasse + ' ' \
        + adresse2.hausnummer + ', ' \
        + adresse2.plz + ' ' \
        + adresse2.stadt

    directions_result = gmaps.directions(adresse1_string,
                                         adresse2_string,
                                         mode="transit",
                                         departure_time=timezone.now())

    distance = directions_result[0]['legs'][0]['distance']['value'] / 1000
    duration = round(directions_result[0]['legs'][0]['duration']['value'] / 60 + 0.5)

    weg = Weg(adresse1=adresse1, adresse2=adresse2, entfernung=distance, dauer_in_minuten=duration)
    weg.save()

    return weg.pk


def get_weg_id(adresse1, adresse2):
    # prüfen ob weg in Modell wege vorhanden
    wege = Weg.objects.filter(adresse1=adresse1, adresse2=adresse2) | Weg.objects.filter(adresse1=adresse2,
                                                                                         adresse2=adresse1)
    # print(wege)
    if wege:
        return wege[0].pk
    else:
        return make_weg(adresse1, adresse2)
    # bei bedarf insert, werte für weg + zeit per google api ermitteln


class EinkommenssteuerView(LoginRequiredMixin, TemplateView):
    model = Schicht
    context_object_name = 'einkommenssteuer'
    template_name = 'assistenten/einkommenssteuer.html'
    act_year = timezone.now().year
    wege = {}
    abwesenheit = {}

    def get_context_data(self, **kwargs):
        startjahr = self.request.user.assistent.einstellungsdatum.year
        endjahr = self.act_year
        jahre = {jahr: str(jahr) for jahr in range(startjahr, endjahr + 1)}
        jahre[-1] = 'Jahr auswählen'
        context = super().get_context_data(**kwargs)
        context['jahre'] = jahre

        if 'jahreswaehler' in self.request.GET:
            if int(self.request.GET['jahreswaehler']) in range(1900, 2200):
                self.act_year = int(self.request.GET['jahreswaehler'])
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
        # um die schichten manipipulierbar zu machen, werden sie direkt in eine Liste gepackt.
        schichten = list(
            Schicht.objects.filter(beginn__year=self.act_year) | Schicht.objects.filter(ende__year=self.act_year)
        )

        # prüfen ob der hauptanteil der randschichten im aktuellen jahr liegt.
        # wenn nicht fliegt die schicht aus der liste
        for schicht in schichten:
            if schicht.beginn.year != schicht.ende.year:
                if get_schicht_hauptanteil(schicht).year != self.act_year:
                    schichten.remove(schicht)

        user_home = Adresse.objects.get(assistent=self.request.user.assistent, is_home=True)
        # TODO Stufen für Verpflegungsmehraufwand aus DB
        stufen = {0: 0, 8: 0, 24: 0}
        for schicht in schichten:
            dauer = get_duration(schicht.beginn, schicht.ende, 'minutes')
            # hinweg
            weg_id = get_weg_id(adresse1=user_home, adresse2=schicht.beginn_adresse)
            weg = Weg.objects.get(pk=weg_id)
            dauer += weg.dauer_in_minuten
            # print(weg)
            if weg_id not in self.wege:
                self.wege[weg_id] = 1
            else:
                self.wege[weg_id] += 1
            # rückweg
            weg_id = get_weg_id(adresse1=schicht.ende_adresse, adresse2=user_home)
            weg = Weg.objects.get(pk=weg_id)
            dauer += weg.dauer_in_minuten
            # print(weg)
            if weg_id not in self.wege:
                self.wege[weg_id] = 1
            else:
                self.wege[weg_id] += 1

            schicht_stufe = 0
            if dauer/60 > 24

            for stufe in stufen.keys():
                if dauer / 60 >= float(stufe):
                    schicht_stufe = stufe
            if schicht_stufe not in stufen:
                stufen[schicht_stufe] = 1
            else:
                stufen[schicht_stufe] += 1

        print(stufen)
        print(self.wege)
