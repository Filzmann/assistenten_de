from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from guardian.mixins import PermissionRequiredMixin

from assistenten.models import Assistent
from assistenten.forms import AsEditAsMultiForm


class AsEditAssistentView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    template_name = "assistenten/edit_assistent.html"
    form_class = AsEditAsMultiForm
    model = Assistent
    success_url = reverse_lazy('index')
    permission_required = 'change_assistent'

    def get_form_kwargs(self):
        kwargs = super(AsEditAssistentView, self).get_form_kwargs()
        kwargs.update(instance={
            'assistent': self.object,
            'adresse': self.object.adressen.all().filter(is_home=True)[0]
        })
        return kwargs

