from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from guardian.mixins import PermissionRequiredMixin

from assistenten.forms.asn_edit_asn_multiform import AsnEditAsnMultiForm
from assistenten.models import ASN
from assistenten.forms import AsEditAsMultiForm


class AsnEditAsnView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    template_name = "assistenten/asn_edit_asn.html"
    form_class = AsnEditAsnMultiForm
    model = ASN
    success_url = reverse_lazy('index')
    permission_required = 'change_asn'

    def get_form_kwargs(self):
        kwargs = super(AsnEditAsnView, self).get_form_kwargs()
        kwargs.update(instance={
            'asn': self.object,
            'adresse': self.object.adressen.all().filter(is_home=True)[0]
        })
        return kwargs
