from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from assistenten.forms.edit_au import EditAUForm
from assistenten.models import AU


class CreateAUView(LoginRequiredMixin, CreateView):
    template_name = "assistenten/edit_au.html"
    form_class = EditAUForm
    model = AU
    success_url = reverse_lazy('schicht_tabelle')

    def form_valid(self, form):

        au = form.save(commit=False)
        assistent = self.request.user.assistent
        au.assistent = assistent
        au.save()

        return redirect('schicht_tabelle', year=au.beginn.year, month=str(au.beginn.month).zfill(2))


class EditAUView(LoginRequiredMixin, UpdateView):
    template_name = "assistenten/edit_au.html"
    form_class = EditAUForm
    model = AU
    success_url = reverse_lazy('schicht_tabelle')


class DeleteAUView(LoginRequiredMixin, DeleteView):
    model = AU
    success_url = reverse_lazy('schicht_tabelle')
