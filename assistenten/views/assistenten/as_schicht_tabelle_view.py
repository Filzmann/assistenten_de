from datetime import timedelta
from django.utils.datetime_safe import datetime

from assistenten.functions.schicht_functions import berechne_sa_so_weisil_feiertagszuschlaege, berechne_stunden, \
    berechne_urlaub_au_saetze, brutto_in_db, get_lohn, get_nachtstunden, get_sliced_schichten_by_as, sort_schicht_data_by_beginn, add_feste_schichten_as
from assistenten.models import Urlaub, AU
from assistenten.functions.calendar_functions import check_feiertag, get_monatserster, get_first_of_next_month, \
    shift_month, calc_freie_sonntage
from assistenten.views.abstract_dienstplan_view import AbstractDienstplanView


class AsSchichtTabellenView(AbstractDienstplanView):
    context_object_name = 'as_schicht_tabellen_monat'
    template_name = 'assistenten/assistenten/show_AsSchichtTabelle.html'
    summen = {}

    def get_context_data(self, **kwargs):
        self.assistent = self.request.user.assistent
        self.reset()
        # Call the base implementation first to get a context
        context = super(AsSchichtTabellenView, self).get_context_data(**kwargs)
        self.calc_add_sum_data()
        context['summen'] = self.summen
        # brutto in db speichern
        brutto_in_db(
            brutto=self.summen['bruttolohn'],
            stunden=self.summen['arbeitsstunden'],
            monat=self.act_date,
            assistent=self.request.user.assistent
        )
        self.reset()
        return context

    def calc_add_sum_data(self):
        self.calc_freizeitausgleich()
        self.calc_ueberstunden_zuschlag()
        self.summen['freie_sonntage'] = calc_freie_sonntage(act_date=self.act_date, assistent=self.assistent)
        self.summen['moegliche_arbeitssonntage'] = self.summen['freie_sonntage'] - 15
        self.summen['bruttolohn'] = float(
            self.summen['lohn']) + float(
            self.summen['nachtzuschlag_kumuliert']) + float(
            self.summen['orga_zuschlag_kumuliert']) + float(
            self.summen['wechselschicht_zuschlag_kumuliert']) + float(
            self.summen['bsd_kumuliert']) + float(
            self.summen['urlaubslohn']) + float(
            self.summen['aulohn']) + float(
            self.summen['freizeitausgleich']) + float(
            self.summen['ueberstunden_kumuliert'])

        for zuschlag in self.summen['zuschlaege'].values():
            self.summen['bruttolohn'] += float(zuschlag['kumuliert'])

    def calc_freizeitausgleich(self):
        # anzahl aller feiertage ermitteln
        start = get_monatserster(self.act_date)
        end = get_first_of_next_month(start)

        letzter_tag = (end - timedelta(seconds=1)).day
        ausgleichsstunden = berechne_urlaub_au_saetze(datum=start,
                                                      assistent=self.assistent)['stunden_pro_tag']
        ausgleichslohn = berechne_urlaub_au_saetze(datum=start,
                                                   assistent=self.assistent)['pro_stunde']
        for tag in range(1, letzter_tag + 1):
            if check_feiertag(datetime(year=start.year, month=start.month, day=tag)):
                self.summen['anzahl_feiertage'] += 1
                self.summen['freizeitausgleich'] += ausgleichslohn * ausgleichsstunden

    def calc_ueberstunden_zuschlag(self):
        # überstunden
        ueberstunden = self.summen['arbeitsstunden'] + self.summen['urlaubsstunden'] + self.summen['austunden'] - 168.5
        if ueberstunden > 0:
            lohn = get_lohn(assistent=self.request.user.assistent, datum=self.act_date)
            self.summen['ueberstunden'] = ueberstunden
            self.summen['ueberstunden_pro_stunde'] = float(lohn.ueberstunden_zuschlag)
            self.summen['ueberstunden_kumuliert'] = float(lohn.ueberstunden_zuschlag) * ueberstunden

    def calc_schichten(self, start, ende):
        # feste Schichten
        add_feste_schichten_as(erster_tag=start, letzter_tag=ende, assistent=self.request.user.assistent)

        schichten = get_sliced_schichten_by_as(
            start=self.act_date,
            end=ende,
            assistent=self.assistent
        )

        for schicht in schichten:
            if not schicht['beginn'].strftime('%d') in self.schichten_view_data.keys():
                self.schichten_view_data[schicht['beginn'].strftime('%d')] = []

            schicht_id = schicht['schicht_id']
            # zusätzlich
            # at etc
            asn_add = ''
            asn_add += 'AT ' if 'ist_assistententreffen' in schicht and schicht['ist_assistententreffen'] else ''
            asn_add += 'PCG ' if 'ist_pcg' in schicht and schicht['ist_pcg'] else ''
            asn_add += 'RB/BSD ' if 'ist_kurzfristig' in schicht and schicht['ist_kurzfristig'] else ''
            asn_add += 'AFG ' if 'ist_ausfallgeld' in schicht and schicht['ist_ausfallgeld'] else ''

            # stunden
            stunden = berechne_stunden(schicht)

            lohn = get_lohn(assistent=self.assistent, datum=schicht['beginn'])

            nachtstunden = get_nachtstunden(schicht)

            # zuschläge
            zuschlaege = berechne_sa_so_weisil_feiertagszuschlaege(schicht)
            zuschlaege_text = ''

            if zuschlaege:
                if zuschlaege['stunden_gesamt'] > 0:
                    grund = zuschlaege['zuschlagsgrund']
                    # Grund zu lower-case mit "_" statt " " und ohne punkte,
                    # damit es dem Spaltennamen der Tabelle entspricht
                    grund_formatiert = grund.lower().replace('.', '').replace(' ', '_')
                    spaltenname = grund_formatiert + '_zuschlag'
                    stundenzuschlag = float(getattr(lohn, spaltenname))
                    schichtzuschlag = zuschlaege['stunden_gesamt'] * stundenzuschlag
                    zuschlaege_text = grund + ': ' + "{:,.2f}".format(
                        zuschlaege['stunden_gesamt']
                    ) + ' Std = ' + "{:,.2f}€".format(schichtzuschlag)

                    # in Summen
                    # print(self.summen['zuschlaege'])
                    if grund_formatiert in self.summen['zuschlaege']:
                        self.summen['zuschlaege'][grund_formatiert]["stunden"] += zuschlaege['stunden_gesamt']
                        self.summen['zuschlaege'][grund_formatiert]["kumuliert"] += schichtzuschlag
                    else:
                        self.summen['zuschlaege'][grund_formatiert] = \
                            {
                                'bezeichner': grund,
                                'stunden': zuschlaege['stunden_gesamt'],
                                'pro_stunde': stundenzuschlag,
                                'kumuliert': schichtzuschlag
                            }

            asn_add += schicht['asn'].kuerzel if schicht['asn'] else ''
            self.schichten_view_data[schicht['beginn'].strftime('%d')].append(
                {
                    'schicht_id': schicht_id,
                    'von': schicht['beginn'],
                    'bis': schicht['ende'],
                    'asn': asn_add,
                    'stunden': stunden,
                    'stundenlohn': lohn.grundlohn,
                    'schichtlohn': float(lohn.grundlohn) * stunden,
                    'bsd': float(lohn.grundlohn) * stunden * (
                            lohn.kurzfristig_zuschlag_prozent / 100) if 'ist_kurzfristig' in schicht and schicht[
                        'ist_kurzfristig'] else 0,
                    'orgazulage': lohn.orga_zuschlag,
                    'orgazulage_schicht': float(lohn.orga_zuschlag) * stunden,
                    'wechselzulage': lohn.wechselschicht_zuschlag,
                    'wechselzulage_schicht': float(lohn.wechselschicht_zuschlag) * stunden,
                    'nachtstunden': nachtstunden,
                    'nachtzuschlag': lohn.nacht_zuschlag,
                    'nachtzuschlag_schicht': float(lohn.nacht_zuschlag) * nachtstunden,
                    'zuschlaege': zuschlaege_text,
                    'type': 'schicht'
                }
            )

            # daten für Summen-Tabelle

            self.summen['arbeitsstunden'] += stunden
            self.summen['stundenlohn'] = lohn.grundlohn
            self.summen['lohn'] += stunden * float(lohn.grundlohn)
            self.summen['nachtstunden'] += nachtstunden
            self.summen['nachtzuschlag'] = lohn.nacht_zuschlag
            self.summen['nachtzuschlag_kumuliert'] += nachtstunden * float(lohn.nacht_zuschlag)
            self.summen['bsd_stunden'] += stunden if 'ist_kurzfristig' in schicht and schicht['ist_kurzfristig'] else 0
            self.summen['bsd_lohn'] = (lohn.kurzfristig_zuschlag_prozent / 100) * lohn.grundlohn \
                if 'ist_kurzfristig' in schicht and schicht['ist_kurzfristig'] else 0
            self.summen['bsd_kumuliert'] += (float(
                lohn.kurzfristig_zuschlag_prozent / 100 * lohn.grundlohn) * stunden) \
                if 'ist_kurzfristig' in schicht and schicht['ist_kurzfristig'] else 0
            # self.summen['bsd_wegegeld'] += 0  # TODO
            self.summen['orga_zuschlag'] = lohn.orga_zuschlag
            self.summen['orga_zuschlag_kumuliert'] += float(lohn.orga_zuschlag) * stunden
            self.summen['wechselschicht_zuschlag'] = lohn.wechselschicht_zuschlag
            self.summen['wechselschicht_zuschlag_kumuliert'] += float(lohn.wechselschicht_zuschlag) * stunden

        # Deckelung des Wechselschichtzuschlages:
        if self.summen['wechselschicht_zuschlag_kumuliert'] > 105:
            self.summen['wechselschicht_zuschlag_kumuliert'] = 105
            # mehrere Schichten an jedem Tag nach schichtbeginn sortieren
        for key in self.schichten_view_data:
            self.schichten_view_data[key] = sort_schicht_data_by_beginn(self.schichten_view_data[key])

    def calc_urlaube(self, start, ende):
        # Urlaube ermitteln
        # es soll kein urlaub gefunden werden, der genau am nächsten monatsersten um 0:00 Uhr beginnt
        ende = ende - timedelta(minutes=2)
        # finde alle urlaube, der anfang, ende oder mitte (anfang ist vor beginn und ende nach ende dieses Monats)
        # in diesem Urlaub liegt
        urlaube = \
            Urlaub.objects.filter(beginn__range=(start, ende)).filter(assistent=self.request.user.assistent) | \
            Urlaub.objects.filter(ende__range=(start, ende)).filter(assistent=self.request.user.assistent) | \
            Urlaub.objects.filter(beginn__lte=start).filter(
                ende__gte=ende).filter(assistent=self.request.user.assistent)

        for urlaub in urlaube:
            erster_tag = urlaub.beginn.day if urlaub.beginn > start.date() else start.day
            letzter_tag = urlaub.ende.day if urlaub.ende < ende.date() else (ende - timedelta(days=1)).day
            urlaubsstunden = berechne_urlaub_au_saetze(datum=start,
                                                       assistent=self.request.user.assistent)['stunden_pro_tag']
            urlaubslohn = berechne_urlaub_au_saetze(datum=start,
                                                    assistent=self.request.user.assistent)['pro_stunde']
            for tag in range(erster_tag, letzter_tag + 2):
                # print(tag)
                if tag not in self.schichten_view_data.keys():
                    self.schichten_view_data["{:02d}".format(tag)] = []
                self.schichten_view_data["{:02d}".format(tag)].append(
                    {
                        'schicht_id': urlaub.id,
                        'von': '',
                        'bis': '',
                        'asn': 'Urlaub',
                        'stunden': urlaubsstunden,
                        'stundenlohn': urlaubslohn,
                        'schichtlohn': urlaubslohn * urlaubsstunden,
                        'bsd': 0,
                        'orgazulage': 0,
                        'orgazulage_schicht': 0,
                        'wechselzulage': 0,
                        'wechselzulage_schicht': 0,
                        'nachtstunden': 0,
                        'nachtzuschlag': 0,
                        'nachtzuschlag_schicht': 0,
                        'zuschlaege': 0,
                        'type': 'urlaub'
                    }
                )

                self.summen['urlaubsstunden'] += urlaubsstunden
                self.summen['stundenlohn_urlaub'] = urlaubslohn
                self.summen['urlaubslohn'] += urlaubsstunden * urlaubslohn

    def calc_au(self, start, ende):
        # AU ermitteln

        # es soll keine au gefunden werden, die genau am nächsten monatsersten um 0:00 Uhr beginnt
        ende = ende - timedelta(minutes=2)
        # finde alle AU, der anfang, ende oder mitte (anfang ist vor beginn und ende nach ende dieses Monats)
        # in diesem AU liegt
        aus = \
            AU.objects.filter(beginn__range=(start, ende)).filter(assistent=self.request.user.assistent) | \
            AU.objects.filter(ende__range=(start, ende)).filter(assistent=self.request.user.assistent) | \
            AU.objects.filter(beginn__lte=start).filter(ende__gte=ende).filter(assistent=self.request.user.assistent)

        for au in aus:
            erster_tag = au.beginn.day if au.beginn > start.date() else start.day
            letzter_tag = au.ende.day if au.ende < ende.date() else (ende - timedelta(days=1)).day
            austunden = berechne_urlaub_au_saetze(datum=start,
                                                  assistent=self.request.user.assistent)['stunden_pro_tag']
            aulohn = berechne_urlaub_au_saetze(datum=start,
                                               assistent=self.request.user.assistent)['pro_stunde']

            for tag in range(erster_tag, letzter_tag + 1):
                # print(tag)
                if tag not in self.schichten_view_data.keys():
                    self.schichten_view_data["{:02d}".format(tag)] = []
                self.schichten_view_data["{:02d}".format(tag)].append(
                    {
                        'schicht_id': au.id,
                        'von': '',
                        'bis': '',
                        'asn': 'AU/krank',
                        'stunden': austunden,
                        'stundenlohn': aulohn,
                        'schichtlohn': aulohn * austunden,
                        'bsd': 0,
                        'orgazulage': 0,
                        'orgazulage_schicht': 0,
                        'wechselzulage': 0,
                        'wechselzulage_schicht': 0,
                        'nachtstunden': 0,
                        'nachtzuschlag': 0,
                        'nachtzuschlag_schicht': 0,
                        'zuschlaege': 0,
                        'type': 'au'
                    }
                )
                self.summen['austunden'] += austunden
                self.summen['stundenlohn_au'] = aulohn
                self.summen['aulohn'] += austunden * aulohn

    def get_table_data(self):
        # TODO optimieren!!!

        start = self.act_date
        ende = get_first_of_next_month(this_month=start)

        # schichten berechnen und in schicht_view_data bzw. summen einsortieren
        self.calc_schichten(start=start, ende=ende)

        # urlaube berechnen und in schicht_view_data bzw. summen einsortieren
        self.calc_urlaube(start=start, ende=ende)

        # au/krank berechnen und in schicht_view_data bzw. summen einsortieren
        self.calc_au(start=start, ende=ende)

        # schichtsammlung durch ergänzung von leeren Tagen zu Kalender konvertieren
        monatsletzter = (shift_month(self.act_date, step=1) - timedelta(days=1)).day
        table_array = {}
        for i in range(1, monatsletzter + 1):
            key = str(i).zfill(2)
            datakey = datetime(year=self.act_date.year, month=self.act_date.month, day=i)
            if key in self.schichten_view_data:
                table_array[datakey] = self.schichten_view_data[key]
            else:
                table_array[datakey] = []

        return table_array

    def reset(self):
        self.schichten_view_data = {}
        self.summen = {
            'arbeitsstunden': 0,
            'stundenlohn': 0,
            'lohn': 0,
            'nachtstunden': 0,
            'nachtzuschlag': 0,
            'nachtzuschlag_kumuliert': 0,
            'bsd': 0,
            'bsd_stunden': 0,
            'bsd_kumuliert': 0,
            'wegegeld_bsd': 0,
            'orga_zuschlag': 0,
            'orga_zuschlag_kumuliert': 0,
            'wechselschicht_zuschlag': 0,
            'wechselschicht_zuschlag_kumuliert': 0,
            'freizeitausgleich': 0,
            'bruttolohn': 0,
            'anzahl_feiertage': 0,
            'freie_sonntage': 52,
            'moegliche_arbeitssonntage': 37,
            'urlaubsstunden': 0,
            'stundenlohn_urlaub': 0,
            'urlaubslohn': 0,
            'austunden': 0,
            'stundenlohn_au': 0,
            'aulohn': 0,
            'ueberstunden': 0,
            'ueberstunden_pro_stunde': 0,
            'ueberstunden_kumuliert': 0,
            'zuschlaege': {}
        }
