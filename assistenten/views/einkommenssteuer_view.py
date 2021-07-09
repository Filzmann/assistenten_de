import googlemaps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import TemplateView

from assistenten.models import Schicht, Adresse, Weg
from assistenten.views.as_schicht_tabelle_view import split_by_null_uhr, get_duration
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

    if directions_result:
        distance = directions_result[0]['legs'][0]['distance']['value'] / 1000
        duration = round(directions_result[0]['legs'][0]['duration']['value'] / 60 + 0.5)

        weg = Weg(adresse1=adresse1, adresse2=adresse2, entfernung=distance, dauer_in_minuten=duration)
        weg.save()

        return weg.pk
    else:
        return False


def get_weg_id(adresse1, adresse2):
    # prüfen ob weg in Modell wege vorhanden
    wege = Weg.objects.filter(adresse1=adresse1, adresse2=adresse2) | Weg.objects.filter(adresse1=adresse2,
                                                                                         adresse2=adresse1)
    # print(wege)
    if wege:
        return wege[0].pk
    else:
        weg = make_weg(adresse1, adresse2)
        if weg:
            return weg
        else:
            return False
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
        self.reset()
        self.calculate_wege()
        context['wege'] = self.wege
        context['abwesenheit'] = self.abwesenheit
        self.reset()
        return context

        # print(GOOGLE_API_KEY)

    def reset(self):
        self.wege = {}
        self.abwesenheit = {}

    def calculate_wege(self):
        # TODO kombinierte Schichten beachten
        # alle Schichten aus dem gewählten Jahr
        # um die schichten manipipulierbar zu machen, werden sie direkt in eine Liste gepackt.
        weg = False
        schichten = list(
            Schicht.objects.filter(beginn__year=self.act_year).filter(assistent=self.request.user.assistent) |
            Schicht.objects.filter(ende__year=self.act_year).filter(assistent=self.request.user.assistent)
        )

        # prüfen ob der hauptanteil der randschichten im aktuellen jahr liegt.
        # wenn nicht fliegt die schicht aus der liste
        for schicht in schichten:
            if schicht.beginn.year != schicht.ende.year:
                if get_schicht_hauptanteil(schicht).year != self.act_year:
                    schichten.remove(schicht)

        user_home = Adresse.objects.get(assistent=self.request.user.assistent, is_home=True)
        if user_home.strasse == '' or user_home.plz == '':
            redirect('schicht_tabelle')

        # TODO Stufen für Verpflegungsmehraufwand aus DB
        stufen = {0: 0, 8: 0, 24: 0}
        an_abfahrten = 0
        for schicht in schichten:
            dauer = get_duration(schicht.beginn, schicht.ende, 'minutes')
            # TODO bessere Lösung als einfach nur weiterleiten bei fehlender Adresse
            if schicht.beginn_adresse.strasse == '' or schicht.beginn_adresse.plz == '':
                redirect('edit_asn', schicht.asn.pk)
            if schicht.ende_adresse.strasse == '' or schicht.ende_adresse.plz == '':
                redirect('edit_asn', schicht.asn.pk)

            # hinweg
            weg_id = get_weg_id(adresse1=user_home, adresse2=schicht.beginn_adresse)
            if weg_id:
                weg = Weg.objects.get(pk=weg_id)
                dauer += weg.dauer_in_minuten
            else:
                weg_id = 0
                dauer = 0

            # print(weg)
            if weg_id not in self.wege:
                self.wege[weg_id] = {'count': 1, 'weg': weg}
            else:
                self.wege[weg_id]['count'] += 1
            # rückweg
            weg_id = get_weg_id(adresse1=schicht.ende_adresse, adresse2=user_home)
            if weg_id:
                weg = Weg.objects.get(pk=weg_id)
                dauer += weg.dauer_in_minuten
            else:
                weg_id = 0
                dauer = 0

            if weg_id not in self.wege:
                self.wege[weg_id] = {'count': 1, 'weg': weg, }
            else:
                self.wege[weg_id]['count'] += 1

            schicht_stufe = 0
            if dauer / 60 >= 48:
                # Reisebegleitung
                dm = divmod(dauer / 60, 24)
                anzahl_24 = dm[0]
                if dm[1] == 0:
                    anzahl_24 -= 1
                stufen[24] += anzahl_24
                an_abfahrten += 2
            else:
                # normale schichten unter 48 Stunden
                for stufe in stufen.keys():
                    if dauer / 60 >= float(stufe):
                        schicht_stufe = stufe
                if schicht_stufe not in stufen:
                    stufen[schicht_stufe] = 1
                else:
                    stufen[schicht_stufe] += 1

        self.abwesenheit = {
            'über 8 Stunden': stufen[8],
            'über 24 Stunden (Reise)': stufen[24],
            'An-/Abreisetage': an_abfahrten
        }

        # Berechnung der km-Pauschale
        # TODO für einige Jahre haben wege über 21 km eine erhöhte Pauschale.

        self.wege.pop('0', 0)

        for weg_id in self.wege:
            self.wege[weg_id]['formel'] = \
                str(self.wege[weg_id]['count']) + ' * ' + str(self.wege[weg_id]['weg'].entfernung) + 'km * 0.30 € '
            self.wege[weg_id]['pauschale'] = \
                self.wege[weg_id]['count'] * float(self.wege[weg_id]['weg'].entfernung) * 0.3
