from django.urls import reverse_lazy

from assistenten.forms.asn.asn_edit_schicht_multiform import AsnCreateSchichtMultiForm, AsnEditSchichtMultiForm
from assistenten.views.edit_schicht_view import CreateSchichtView, EditSchichtView


class EbCreateSchichtView(CreateSchichtView):
    template_name = "assistenten/ebs/eb_edit_schicht.html"
    form_class = AsnCreateSchichtMultiForm
    success_url = reverse_lazy('eb_edit_schicht')


class EbEditSchichtView(EditSchichtView):
    template_name = "assistenten/ebs/eb_edit_schicht.html"
    form_class = AsnEditSchichtMultiForm
    success_url = reverse_lazy('eb_edit_schicht')
