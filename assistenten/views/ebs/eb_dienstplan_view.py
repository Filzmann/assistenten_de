from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.utils.datetime_safe import datetime
from django.views.generic import TemplateView
from guardian.shortcuts import get_objects_for_user

from assistenten.functions.schicht_functions import get_sliced_schichten_by_asn, add_feste_schichten_asn, \
    sort_schicht_data_by_beginn, sort_schichten_in_templates
from assistenten.models import Schicht, ASN
from assistenten.functions.calendar_functions import get_monatserster, get_first_of_next_month, shift_month


class EbDienstplanView(LoginRequiredMixin, TemplateView):
    model = Schicht
    context_object_name = 'eb_dienstplan_monat'
    template_name = 'assistenten/ebs/show_dienstplan.html'
    act_date = timezone.now()
    asn = None
    assistent = None
    schichten_view_data = {}

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
        asn_liste = []
        asns = get_objects_for_user(self.request.user, 'view_asn', klass=ASN, with_superuser=False)
        for asn in asns:
            asn_liste.append((asn.id, asn.kuerzel))
        kwargs['asn_liste'] = asn_liste
        context['schichttabelle'] = self.get_table_data()
        context['first_of_month'] = self.act_date
        context['days_before_first'] = (int(self.act_date.strftime("%w")) + 6) % 7
        context['templates'], context['schichten_nach_templates'] = sort_schichten_in_templates(
            self.asn, self.act_date) if self.asn else [], []

        self.reset()
        return context

    def calc_schichten(self, start, ende):

        schichten = []
        # feste Schichten
        if self.asn:
            add_feste_schichten_asn(erster_tag=start, letzter_tag=ende, asn=self.asn)

            schichten = get_sliced_schichten_by_asn(
                start=self.act_date,
                end=ende,
                asn=self.asn
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
