from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.datetime_safe import datetime
from django.views.generic import UpdateView, CreateView, DeleteView
from django.shortcuts import redirect
from assistenten.forms.assistent.as_edit_schicht_multiform import AsCreateSchichtMultiForm, AsEditSchichtMultiForm
from assistenten.models import Schicht, Adresse, ASN

# TODO beim Eintragen von Schichten über den Jahreswechsel werden daten falsch übernommen.
# Vermutlich im Javascript zur Templateübernahme
from assistenten.views.edit_schicht_view import CreateSchichtView, EditSchichtView


class AsCreateSchichtView(CreateSchichtView):
    template_name = "assistenten/assistenten/as_edit_schicht.html"
    form_class = AsCreateSchichtMultiForm
    asn = None
    assistent = None

    def get_form_kwargs(self):
        self.assistent = self.request.user.assistent
        kwargs = super(AsCreateSchichtView, self).get_form_kwargs()
        return kwargs

    def get_success_url(self, schicht_id):
        redirect('as_edit_schicht', pk=schicht_id)


class AsEditSchichtView(EditSchichtView):
    template_name = "assistenten/assistenten/as_edit_schicht.html"
    form_class = AsEditSchichtMultiForm
    success_url = reverse_lazy('edit_schicht')
    asn = None
    assistent = None

    def form_valid(self, form):
        schicht = form['schicht'].save(commit=False)
        schicht.save()

        if 'just_save' in self.request.POST:
            return redirect('as_schicht_tabelle', year=schicht.beginn.year, month=schicht.beginn.month)
        elif 'save_and_new' in self.request.POST:
            return redirect('as_create_schicht', y=schicht.beginn.year, m=schicht.beginn.month, d=schicht.beginn.day)
        else:
            return redirect('as_edit_schicht', pk=schicht.id)


class DeleteSchichtView(LoginRequiredMixin, DeleteView):
    model = Schicht
    success_url = reverse_lazy('as_schicht_tabelle')

    def get_success_url(self):
        usergroup = self.request.user.groups.values_list('name', flat=True).first()
        if usergroup == "Assistenten":
            return reverse_lazy('as_schicht_tabelle')
        elif usergroup == "Assistenznehmer":
            return reverse_lazy('asn_dienstplan')
