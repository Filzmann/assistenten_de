from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from assistenten.forms.edit_sperrzeiten import FesteSperrzeitForm
from assistenten.functions.schicht_functions import get_sperrzeiten
from assistenten.models import FesteSperrzeit


class CreateFesteSperrzeitView(LoginRequiredMixin, CreateView):
    template_name = "assistenten/edit_feste_sperrzeit.html"
    form_class = FesteSperrzeitForm
    model = FesteSperrzeit
    success_url = reverse_lazy('create_feste_sperrzeit')

    def get_context_data(self, **kwargs):
        kwargs['sperrzeiten_liste'] = get_sperrzeiten(self.request.user, fest=True)
        context = super(CreateFesteSperrzeitView, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):

        feste_sperrzeit = form.save(commit=False)
        usergroup = self.request.user.groups.values_list('name', flat=True).first()
        if usergroup == "Assistenten":
            feste_sperrzeit.assistent = self.request.user.assistent
        elif usergroup == "Assistenznehmer":
            feste_sperrzeit.asn = self.request.user.assistenznehmer
        feste_sperrzeit.save()

        return super().form_valid(form)


class EditFesteSperrzeitView(LoginRequiredMixin, UpdateView):
    template_name = "assistenten/edit_feste_sperrzeit.html"
    form_class = FesteSperrzeitForm
    model = FesteSperrzeit
    success_url = reverse_lazy('edit_feste_sperrzeit')

    def get_context_data(self, **kwargs):
        kwargs['sperrzeiten_liste'] = get_sperrzeiten(self.request.user, fest=True)
        context = super(EditFesteSperrzeitView, self).get_context_data(**kwargs)
        return context


class DeleteFesteSperrzeitView(LoginRequiredMixin, DeleteView):
    model = FesteSperrzeit
    success_url = reverse_lazy('create_feste_sperrzeit')
