from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from assistenten.models import Schicht


class AsSchichtTabellenView(LoginRequiredMixin, ListView):
    model = Schicht
    context_object_name = 'as_schicht_tabellen_monat'
    template_name = 'assistenten/show_AsSchichtTabelle.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['nav_timedelta'] = 'nav timedelta'
        context['summen'] = 'summen'
        context['schichten'] = Schicht.objects.all()
        return context
