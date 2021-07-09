from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, DeleteView
from guardian.mixins import PermissionRequiredMixin
from assistenten.forms.asn_edit_asn_multiform import AsnEditAsnMultiForm
from assistenten.functions.schicht_functions import get_schicht_templates
from assistenten.models import ASN, SchichtTemplate


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
            'adresse': self.object.adressen.all().filter(is_home=True)[0],
        })
        print(kwargs)
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs['schicht_template_liste'] = get_schicht_templates(self.object)
        context = super(AsnEditAsnView, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        asn = form['asn'].save()
        adresse = form['adresse'].save(commit=False)
        adresse.asn = asn
        adresse.is_home = True
        adresse.save()

        schicht_template = form['asn_schicht_templates'].save(commit=False)
        if schicht_template.bezeichner != '':
            schicht_template.asn = asn
            schicht_template.save()

        return redirect('asn_edit_asn', pk=asn.id)


