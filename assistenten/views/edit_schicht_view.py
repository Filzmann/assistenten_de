from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from assistenten.models import Schicht


class EditAssistentView(LoginRequiredMixin, UpdateView):
    template_name = "assistenten/edit_assistent.html"
    form_class = EditSchichtMultiForm
    model = Schicht
    success_url = reverse_lazy('index')

    def get_form_kwargs(self):
        kwargs = super(EditAssistentView, self).get_form_kwargs()
        kwargs.update(instance={
            'assistent': self.object,
            'adresse': self.object.adressen.all().filter(is_home=True)[0]
        })
        return kwargs
