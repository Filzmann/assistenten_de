from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import request
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, CreateView

from assistenten.forms.edit_asn_multiform import EditAsnMultiForm
from assistenten.models import ASN, Assistent


def get_asn_liste(assistent: Assistent):
    asnliste = assistent.asns.all()
    print(asnliste)


class CreateAsnView(LoginRequiredMixin, CreateView):
    template_name = "assistenten/edit_asn.html"
    form_class = EditAsnMultiForm
    model = ASN
    success_url = reverse_lazy('index')

    # For Create
    def get_context_data(self, **kwargs):
        kwargs['asn_liste'] = [(1, 'hawefu'), (2, 'ThoJa'), (3, 'MaPu')]
        context = super(CreateAsnView, self).get_context_data(**kwargs)
        return context


class EditAsnView(LoginRequiredMixin, UpdateView):
    template_name = "assistenten/edit_asn.html"
    form_class = EditAsnMultiForm
    model = ASN
    success_url = reverse_lazy('index')

    def get_form_kwargs(self):
        kwargs = super(EditAsnView, self).get_form_kwargs()
        kwargs.update(instance={
            'asn': self.object,
            'adresse': self.object.adressen.all().filter(is_home=True)[0]
        })
        return kwargs

    # For Update
    def get_context_data(self, **kwargs):
        kwargs['asn_liste'] = [(1, 'hawefu'), (2, 'ThoJa'), (3, 'MaPu')]
        context = super(EditAsnView, self).get_context_data(**kwargs)
        return context
