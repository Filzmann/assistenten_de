from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import request
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, CreateView

from assistenten.forms.edit_asn_multiform import EditAsnMultiForm, CreateAsnMultiForm
from assistenten.models import ASN, Assistent


class CreateAsnView(LoginRequiredMixin, CreateView):
    template_name = "assistenten/edit_asn.html"
    form_class = CreateAsnMultiForm
    model = ASN
    success_url = reverse_lazy('create_asn')

    def get_context_data(self, **kwargs):
        asn_liste = []
        asns = self.request.user.assistent.asns.all()
        for asn in asns:
            asn_liste.append((asn.id, str(asn)))
        kwargs['asn_liste'] = asn_liste
        context = super(CreateAsnView, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        asn = form['asn_stammdaten'].save()
        assistent = self.request.user.assistent

        asn.assistents.add(assistent)
        asn.save()
        adresse = form['asn_adresse'].save(commit=False)
        adresse.asn = asn
        adresse.is_home = True
        adresse.save()
        return redirect(self.get_success_url())


class EditAsnView(LoginRequiredMixin, UpdateView):
    template_name = "assistenten/edit_asn.html"
    form_class = EditAsnMultiForm
    model = ASN
    success_url = reverse_lazy('edit_asn')

    def get_form_kwargs(self):
        kwargs = super(EditAsnView, self).get_form_kwargs()
        kwargs.update(instance={
            'asn': self.object,
            'adresse': self.object.adressen.all().filter(is_home=True)[0]
        })
        return kwargs

    # For Update
    def get_context_data(self, **kwargs):
        asn_liste = []
        asns = self.request.user.assistent.asns.all()
        for asn in asns:
            asn_liste.append((asn.id, str(asn)))
        kwargs['asn_liste'] = asn_liste
        context = super(EditAsnView, self).get_context_data(**kwargs)
        return context
