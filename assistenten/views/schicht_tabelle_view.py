from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import request
from django.utils.datetime_safe import datetime
from django.views.generic import ListView, TemplateView
from assistenten.models import Schicht


def get_monatserster(datum):
    return datetime(year=datum.year,
                    month=datum.month,
                    day=1,
                    )


class AsSchichtTabellenView(LoginRequiredMixin, TemplateView):
    model = Schicht
    context_object_name = 'as_schicht_tabellen_monat'
    template_name = 'assistenten/show_AsSchichtTabelle.html'
    act_date = datetime.now()



    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        print(self.request.GET)
        print(kwargs)
        if 'year' in self.request.GET:
            self.act_date = datetime(year=int(self.request.GET['year']),
                                     month=int(self.request.GET['month']),
                                     day=1)
        elif 'year' in kwargs:
            self.act_date = datetime(year=int(kwargs['year']),
                                     month=int(kwargs['month']),
                                     day=1)

        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['nav_timedelta'] = self.get_time_navigation_data()
        context['summen'] = 'summen'
        context['schichten'] = Schicht.objects.all()
        return context

    def get_time_navigation_data(self, **kwargs):
        if 'act_date' in self.request.POST:
            self.act_date = self.request.POST['act_date']

        if 'year' in self.request.POST:
            self.act_date = datetime(year=self.request.POST['year'],
                                     month=self.request.POST['month'],
                                     day=1
                                     )

        act_date = get_monatserster(self.act_date)

        vormonat = {
            'year': act_date.year,
            'month': act_date.month - 1,

        }
        if vormonat['month'] == 0:
            vormonat['month'] = 12
            vormonat['year'] -= 1

        vormonat_date = datetime(year=vormonat['year'], month=vormonat['month'], day=1)

        nachmonat = {
            'year': act_date.year,
            'month': act_date.month + 1,

        }
        if nachmonat['month'] == 13:
            nachmonat['month'] = 1
            nachmonat['year'] += 1

        nachmonat_date = datetime(year=nachmonat['year'], month=nachmonat['month'], day=1)

        monatsliste = {}
        for i in range(1, 13):
            monatsliste[datetime(month=i,
                                 year=1,
                                 day=1).strftime('%m')] = datetime(month=i,
                                                                   year=1,
                                                                   day=1).strftime('%b')

        jahresliste = []
        for j in range(datetime.now().year + 2, datetime.now().year-40, -1):
            jahresliste.append(str(j))

        return {
            'act_date': act_date,
            'vormonat_date': vormonat_date,
            'nachmonat_date': nachmonat_date,
            'monatsliste': monatsliste,
            'jahresliste': jahresliste
        }
