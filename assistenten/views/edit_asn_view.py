from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from assistenten.models import Assistent, Adresse
from assistenten.forms import EditAsMultiForm


class EditAssistentView(LoginRequiredMixin, UpdateView):
    template_name = "assistenten/edit_assistent.html"
    form_class = EditAsMultiForm
    model = Assistent
    success_url = reverse_lazy('index')

    def get_form_kwargs(self):
        kwargs = super(EditAssistentView, self).get_form_kwargs()
        kwargs.update(instance={
            'assistent': self.object,
            'adresse': self.object.adressen.all().filter(is_home=True)[0]
        })
        return kwargs
