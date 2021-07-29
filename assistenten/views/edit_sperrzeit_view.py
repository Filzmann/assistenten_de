from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from assistenten.forms.edit_sperrzeiten import EditSperrzeitForm
from assistenten.functions.schicht_functions import get_sperrzeiten
from assistenten.models import Sperrzeit


class CreateSperrzeitView(LoginRequiredMixin, CreateView):
    template_name = "assistenten/edit_sperrzeit.html"
    form_class = EditSperrzeitForm
    model = Sperrzeit
    success_url = reverse_lazy('create_sperrzeit')

    def get_context_data(self, **kwargs):
        kwargs['sperrzeiten_liste'] = get_sperrzeiten(self.request.user)
        context = super(CreateSperrzeitView, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):

        sperrzeit = form.save(commit=False)
        usergroup = self.request.user.groups.values_list('name', flat=True).first()
        if usergroup == "Assistenten":
            sperrzeit.assistent = self.request.user.assistent
        elif usergroup == "Assistenznehmer":
            sperrzeit.asn = self.request.user.assistenznehmer
        sperrzeit.save()

        return super().form_valid(form)


class EditSperrzeitView(LoginRequiredMixin, UpdateView):
    template_name = "assistenten/edit_sperrzeit.html"
    form_class = EditSperrzeitForm
    model = Sperrzeit
    success_url = reverse_lazy('edit_feste_sperrzeit')

    def get_context_data(self, **kwargs):
        kwargs['sperrzeiten_liste'] = get_sperrzeiten(self.request.user)
        context = super(EditSperrzeitView, self).get_context_data(**kwargs)
        return context


class DeleteSperrzeitView(LoginRequiredMixin, DeleteView):
    model = Sperrzeit
    success_url = reverse_lazy('create_sperrzeit')
