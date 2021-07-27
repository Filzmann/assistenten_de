from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from assistenten.forms.edit_sperrzeiten import EditSperrzeitForm
from assistenten.forms.edit_urlaub import EditUrlaubForm
from assistenten.models import Urlaub, Sperrzeit


class CreateSperrzeitView(LoginRequiredMixin, CreateView):
    template_name = "assistenten/edit_sperrzeit.html"
    form_class = EditSperrzeitForm
    model = Sperrzeit
    success_url = reverse_lazy('as_schicht_tabelle')

    # def get_success_url(self):
    #     usergroup = self.request.user.groups.values_list('name', flat=True).first()
    #     if usergroup == "Assistenten":
    #         return reverse_lazy("as_schicht_tabelle")
    #     elif usergroup == "Assistenznehmer":
    #         return reverse_lazy("asn_dienstplan")

    def form_valid(self, form):

        sperrzeit = form.save(commit=False)
        usergroup = self.request.user.groups.values_list('name', flat=True).first()
        if usergroup == "Assistenten":
            sperrzeit.assistent = self.request.user.assistent
        elif usergroup == "Assistenznehmer":
            sperrzeit.asn = self.request.user.asn
        sperrzeit.save()

        return self.get_success_url()


class EditSperrzeitView(LoginRequiredMixin, UpdateView):
    template_name = "assistenten/edit_sperrzeit.html"
    form_class = EditSperrzeitForm
    model = Sperrzeit
    success_url = reverse_lazy('as_schicht_tabelle')

    # def get_success_url(self):
    #     usergroup = self.request.user.groups.values_list('name', flat=True).first()
    #     if usergroup == "Assistenten":
    #         return reverse_lazy("as_schicht_tabelle")
    #     elif usergroup == "Assistenznehmer":
    #         return reverse_lazy("asn_dienstplan")


class DeleteSperrzeitView(LoginRequiredMixin, DeleteView):
    model = Sperrzeit
    success_url = reverse_lazy('as_schicht_tabelle')



