from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView

from assistenten.forms.edit_schicht import EditSchichtForm
from assistenten.forms.edit_schicht_multiform import EditSchichtMultiForm
from assistenten.models import Schicht


class CreateSchichtView(LoginRequiredMixin, CreateView):
    template_name = "assistenten/edit_schicht.html"
    form_class = EditSchichtForm
    model = Schicht
    success_url = reverse_lazy('index')

    # def get_form_kwargs(self):
    #     kwargs = super(CreateSchichtView, self).get_form_kwargs()
    #     kwargs.update(instance={
    #         'assistent': self.object,
    #         'adresse': self.object.adressen.all().filter(is_home=True)[0]
    #     })
    #     return kwargs
