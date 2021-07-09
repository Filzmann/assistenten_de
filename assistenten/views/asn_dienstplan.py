from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.utils.datetime_safe import datetime
from django.views.generic import TemplateView
from assistenten.models import Schicht, FesteSchicht, Adresse
from assistenten.views.as_schicht_tabelle_view import get_ersten_xxtag, check_au, check_urlaub, get_monatserster, \
    check_mehrtaegig, sort_schicht_data_by_beginn, get_first_of_next_month, shift_month


def get_sliced_schichten(start, end, asn):
    schichten = \
        Schicht.objects.filter(beginn__range=(start, end)).filter(asn=asn) | \
        Schicht.objects.filter(ende__range=(start, end)).filter(asn=asn)

    sliced_schichten = []
    for schicht in schichten:
        ergebnisse = split_by_null_uhr(schicht)
        for ergebnis in ergebnisse:
            sliced_schichten.append(ergebnis)

    return sliced_schichten


def split_by_null_uhr(schicht):
    ausgabe = []

    if check_mehrtaegig(schicht):
        rest = dict(start=schicht.beginn, ende=schicht.ende)
        while rest['start'] <= rest['ende']:
            r_start = rest['start']
            neuer_start_rest = timezone.make_aware(datetime(year=r_start.year,
                                                            month=r_start.month,
                                                            day=r_start.day
                                                            )) + timedelta(days=1)

            if neuer_start_rest <= rest['ende']:
                ausgabe.append({'beginn': rest['start'],
                                'ende': neuer_start_rest,
                                'asn': schicht.asn,
                                'assistent': schicht.assistent,
                                'schicht_id': schicht.id,
                                'beginn_adresse': schicht.beginn_adresse,
                                'ende_adresse': schicht.ende_adresse
                                })
            else:
                ausgabe.append({'beginn': rest['start'],
                                'ende': rest['ende'],
                                'asn': schicht.asn,
                                'assistent': schicht.assistent,
                                'schicht_id': schicht.id,
                                'beginn_adresse': schicht.beginn_adresse,
                                'ende_adresse': schicht.ende_adresse
                                })

            rest['start'] = neuer_start_rest
    else:
        ausgabe.append({
            'beginn': schicht.beginn,
            'ende': schicht.ende,
            'asn': schicht.asn,
            'assistent': schicht.assistent,
            'schicht_id': schicht.id,
            'beginn_adresse': schicht.beginn_adresse,
            'ende_adresse': schicht.ende_adresse
        })
    return ausgabe


class AsnDienstplanView(LoginRequiredMixin, TemplateView):
    model = Schicht
    context_object_name = 'as_dienstplan_monat'
    template_name = 'assistenten/show_dienstplan.html'
    act_date = timezone.now()
    schichten_view_data = {}

    def add_feste_schichten(self, erster_tag, letzter_tag):
        feste_schichten = FesteSchicht.objects.filter(asn=self.request.user.assistenznehmer)

        for feste_schicht in feste_schichten:
            wtag_int = int(feste_schicht.wochentag)
            erster_xxtag_des_monats = get_ersten_xxtag(wtag_int, erster_tag)
            monat = erster_tag.month
            year = erster_tag.year
            maxday = (letzter_tag - timedelta(days=1)).day
            assi = feste_schicht.assistent
            for woche in range(0, 5):
                tag = woche * 7 + erster_xxtag_des_monats
                if tag <= maxday:
                    if feste_schicht.beginn < feste_schicht.ende:
                        start = timezone.make_aware(datetime(year=year,
                                                             month=monat,
                                                             day=tag,
                                                             hour=feste_schicht.beginn.hour,
                                                             minute=feste_schicht.beginn.minute))
                        end = timezone.make_aware(datetime(year=year,
                                                           month=monat,
                                                           day=tag,
                                                           hour=feste_schicht.ende.hour,
                                                           minute=feste_schicht.ende.minute))
                    # nachtschicht. es gibt keine regelmäßigen dienstreisen!
                    else:
                        start = timezone.make_aware(datetime(year=year,
                                                             month=monat,
                                                             day=tag,
                                                             hour=feste_schicht.beginn.hour,
                                                             minute=feste_schicht.beginn.minute))
                        end = timezone.make_aware(datetime(year=year,
                                                           month=monat,
                                                           day=tag,
                                                           hour=feste_schicht.ende.hour,
                                                           minute=feste_schicht.ende.minute) + timedelta(days=1))
                    if not check_au(datum=start, assistent=assi) and \
                            not check_urlaub(datum=start, assistent=assi) and \
                            not check_au(datum=end - timedelta(minutes=1), assistent=assi) \
                            and not check_urlaub(datum=end - timedelta(minutes=1), assistent=assi):
                        home = Adresse.objects.filter(is_home=True).filter(asn=self.request.user.assistenznehmer)[0]
                        schicht_neu = Schicht(beginn=start,
                                              ende=end,
                                              asn=self.request.user.assistenznehmer,
                                              assistent=assi,
                                              beginn_adresse=home,
                                              ende_adresse=home)
                        schicht_neu.save()

    def get_context_data(self, **kwargs):
        self.reset()
        # Call the base implementation first to get a context
        if 'year' in self.request.GET:
            self.act_date = timezone.make_aware(datetime(year=int(self.request.GET['year']),
                                                         month=int(self.request.GET['month']),
                                                         day=1))
        elif 'year' in kwargs:
            self.act_date = timezone.make_aware(datetime(year=int(kwargs['year']),
                                                         month=int(kwargs['month']),
                                                         day=1))
        else:
            self.act_date = get_monatserster(timezone.now())

        context = super().get_context_data(**kwargs)
        context['nav_timedelta'] = self.get_time_navigation_data()
        context['schichttabelle'] = self.get_table_data()

        self.reset()
        return context

    def calc_schichten(self, start, ende):

        schichten = get_sliced_schichten(
            start=self.act_date,
            end=ende,
            asn=self.request.user.assistenznehmer
        )

        # feste Schichten
        if not schichten:
            self.add_feste_schichten(erster_tag=start, letzter_tag=ende)
            schichten = get_sliced_schichten(
                start=self.act_date,
                end=ende,
                asn=self.request.user.assistenznehmer
            )

        for schicht in schichten:
            if not schicht['beginn'].strftime('%d') in self.schichten_view_data.keys():
                self.schichten_view_data[schicht['beginn'].strftime('%d')] = []

            schicht_id = schicht['schicht_id']
            self.schichten_view_data[schicht['beginn'].strftime('%d')].append(
                {
                    'schicht_id': schicht_id,
                    'von': schicht['beginn'],
                    'bis': schicht['ende'],
                    'assistent': schicht['assistent'].vorname + ' ' + schicht['assistent'].name
                }
            )

        # mehrere Schichten an jedem Tag nach schichtbeginn sortieren
        for key in self.schichten_view_data:
            self.schichten_view_data[key] = sort_schicht_data_by_beginn(self.schichten_view_data[key])

    def get_table_data(self):
        # TODO optimieren!!!

        start = self.act_date
        ende = get_first_of_next_month(this_month=start)

        # schichten berechnen und in schicht_view_data bzw. summen einsortieren
        self.calc_schichten(start=start, ende=ende)

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

    def get_time_navigation_data(self):
        # test
        if 'act_date' in self.request.POST:
            self.act_date = self.request.POST['act_date']

        if 'year' in self.request.POST:
            self.act_date = timezone.make_aware(datetime(year=self.request.POST['year'],
                                                         month=self.request.POST['month'],
                                                         day=1))

        act_date = get_monatserster(self.act_date)
        vormonat_date = shift_month(get_monatserster(self.act_date), step=-1)
        nachmonat_date = shift_month(get_monatserster(self.act_date), step=1)
        monatsliste = {}
        for i in range(1, 13):
            monatsliste[
                datetime(month=i,
                         year=1,
                         day=1).strftime('%m')] = datetime(month=i,
                                                           year=1,
                                                           day=1).strftime('%b')
        jahresliste = []
        for j in range(datetime.now().year + 2, datetime.now().year - 40, -1):
            jahresliste.append(str(j))

        return {
            'act_date': act_date,
            'vormonat_date': vormonat_date,
            'nachmonat_date': nachmonat_date,
            'monatsliste': monatsliste,
            'jahresliste': jahresliste
        }

    def reset(self):
        self.schichten_view_data = {}
