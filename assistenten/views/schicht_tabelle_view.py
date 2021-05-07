from django.contrib.auth.mixins import LoginRequiredMixin
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
            'day:
        }
        if vormonat['month'] == 0:
            vormonat['month'] = 12
            vormonat['jahr'] -= 1



        nachmonat = {
            'year': act_date.year,
            'month': act_date.month + 1,
        }
        if nachmonat['month'] == 13:
            nachmonat['month'] = 1
            nachmonat['jahr'] += 1

        return {
            'act_date': act_date.strftime('%d.%m.%Y'),
            'nachmonat': '.'.join()
                }
