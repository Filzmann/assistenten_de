from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from assistenten.forms.edit_urlaub import EditUrlaubForm
from assistenten.models import Urlaub


class CreateUrlaubView(LoginRequiredMixin, CreateView):
    template_name = "assistenten/edit_urlaub.html"
    form_class = EditUrlaubForm
    model = Urlaub
    success_url = reverse_lazy('as_schicht_tabelle')

    def form_valid(self, form):

        urlaub = form.save(commit=False)
        assistent = self.request.user.assistent
        urlaub.assistent = assistent
        urlaub.save()

        return redirect('as_schicht_tabelle', year=urlaub.beginn.year, month=str(urlaub.beginn.month).zfill(2))


class EditUrlaubView(LoginRequiredMixin, UpdateView):
    template_name = "assistenten/edit_urlaub.html"
    form_class = EditUrlaubForm
    model = Urlaub
    success_url = reverse_lazy('as_schicht_tabelle')


class DeleteUrlaubView(LoginRequiredMixin, DeleteView):
    model = Urlaub
    success_url = reverse_lazy('as_schicht_tabelle')
