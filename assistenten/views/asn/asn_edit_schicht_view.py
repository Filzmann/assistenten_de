from django.shortcuts import redirect
from django.urls import reverse_lazy

from assistenten.forms.asn.asn_edit_schicht_multiform import AsnCreateSchichtMultiForm, AsnEditSchichtMultiForm
from assistenten.views.edit_schicht_view import CreateSchichtView, EditSchichtView


class AsnCreateSchichtView(CreateSchichtView):
    template_name = "assistenten/asn/asn_edit_schicht.html"
    form_class = AsnCreateSchichtMultiForm
    success_url = reverse_lazy('asn_edit_schicht')

    def get_success_url(self, schicht_id):
        redirect('asn_edit_schicht', pk=schicht_id)


class AsnEditSchichtView(EditSchichtView):
    template_name = "assistenten/asn/asn_edit_schicht.html"
    form_class = AsnEditSchichtMultiForm
    success_url = reverse_lazy('asn_edit_schicht')
