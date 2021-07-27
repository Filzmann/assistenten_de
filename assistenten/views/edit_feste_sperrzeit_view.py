from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from assistenten.forms.edit_sperrzeiten import EditSperrzeitForm, FesteSperrzeitForm
from assistenten.forms.edit_urlaub import EditUrlaubForm
from assistenten.models import Urlaub, Sperrzeit, FesteSperrzeit


class CreateFesteSperrzeitView(LoginRequiredMixin, CreateView):
    template_name = "assistenten/edit_sperrzeit.html"
    form_class = FesteSperrzeitForm
    model = FesteSperrzeit
    success_url = reverse_lazy('as_schicht_tabelle')

    def get_success_url(self):
        usergroup = self.request.user.groups.values_list('name', flat=True).first()
        if usergroup == "Assistenten":
            return reverse_lazy("as_schicht_tabelle")
        elif usergroup == "Assistenznehmer":
            return reverse_lazy("asn_dienstplan")

    def form_valid(self, form):

        feste_sperrzeit = form.save(commit=False)
        usergroup = self.request.user.groups.values_list('name', flat=True).first()
        if usergroup == "Assistenten":
            feste_sperrzeit.assistent = self.request.user.assistent
        elif usergroup == "Assistenznehmer":
            feste_sperrzeit.asn = self.request.user.asn
        feste_sperrzeit.save()

        return self.get_success_url(self)


class EditFesteSperrzeitView(LoginRequiredMixin, UpdateView):
    template_name = "assistenten/edit_sperrzeit.html"
    form_class = FesteSperrzeitForm
    model = FesteSperrzeit
    success_url = reverse_lazy('as_schicht_tabelle')

    def get_success_url(self):
        usergroup = self.request.user.groups.values_list('name', flat=True).first()
        if usergroup == "Assistenten":
            return reverse_lazy("as_schicht_tabelle")
        elif usergroup == "Assistenznehmer":
            return reverse_lazy("asn_dienstplan")


class DeleteFesteSperrzeitView(LoginRequiredMixin, DeleteView):
    model = FesteSperrzeit
    success_url = reverse_lazy('as_schicht_tabelle')



