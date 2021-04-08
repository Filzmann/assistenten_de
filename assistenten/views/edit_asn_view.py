from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, CreateView

from assistenten.forms.edit_asn_multiform import EditAsnMultiForm
from assistenten.models import Adresse, ASN
from assistenten.forms import EditAsMultiForm


class CreateAsnView(LoginRequiredMixin, CreateView):
    template_name = "assistenten/edit_asn.html"
    form_class = EditAsnMultiForm
    model = ASN
    success_url = reverse_lazy('index')


class EditAsnView(LoginRequiredMixin, UpdateView):
    template_name = "assistenten/edit_asn.html"
    form_class = EditAsnMultiForm
    model = ASN
    success_url = reverse_lazy('index')

    def get_form_kwargs(self):
        kwargs = super(EditAsnView, self).get_form_kwargs()
        kwargs.update(instance={
            'assistent': self.object,
            'adresse': self.object.adressen.all().filter(is_home=True)[0]
        })
        return kwargs
