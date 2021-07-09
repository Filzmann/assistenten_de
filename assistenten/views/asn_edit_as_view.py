from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from guardian.mixins import PermissionRequiredMixin
from guardian.shortcuts import assign_perm, get_objects_for_user

from assistenten.forms.as_edit_asn_multiform import AsEditAsnMultiForm, AsCreateAsnMultiForm
from assistenten.models import ASN, FesteSchicht, SchichtTemplate, Assistent
from assistenten.functions.schicht_functions import get_schicht_templates, get_feste_schichten


class AsnCreateAsView(LoginRequiredMixin, CreateView):
    template_name = "assistenten/as_edit_asn.html"
    form_class = AsCreateAsnMultiForm
    model = Assistent
    success_url = reverse_lazy('asn_edit_as')

    def get_context_data(self, **kwargs):
        as_liste = []
        assis = get_objects_for_user(self.request.user, 'view_assistent', klass=Assistent, with_superuser=False)

        for assi in assis:
            as_liste.append((assi.id, assi.name + ', ' + assi.vorname))
        kwargs['as_liste'] = as_liste
        context = super(AsnCreateAsView, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        asn = form['as_stammdaten'].save()
        user = self.request.user
        assistent = user.assistent
        asn.assistents.add(assistent)
        asn.save()
        adresse = form['asn_adresse'].save(commit=False)
        adresse.asn = asn
        adresse.is_home = True
        adresse.save()
        # der eingeloggte user erhält das Bearbeitungsrecht
        assign_perm('change_asn', user, asn)
        assign_perm("view_asn", user, asn)

        return redirect('as_edit_asn', pk=asn.id)


class AsnEditAsView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    template_name = "assistenten/as_edit_asn.html"
    form_class = AsEditAsnMultiForm
    model = ASN
    success_url = reverse_lazy('asn_edit_as')
    permission_required = 'change_asn'

    def get_form_kwargs(self):
        kwargs = super(AsnEditAsView, self).get_form_kwargs()
        kwargs.update(instance={
            'asn_stammdaten': self.object,
            'asn_adresse': self.object.adressen.all().filter(is_home=True)[0]
        })
        return kwargs

    # For Update
    def get_context_data(self, **kwargs):

        # alle asn zur auswahl auflisten
        as_liste = []
        assis = get_objects_for_user(self.request.user, 'view_assistent', klass=Assistent, with_superuser=False)

        for assi in assis:
            as_liste.append((assi.id, assi.name + ', ' + assi.vorname))
        kwargs['as_liste'] = as_liste
        # feste schichten und templates gibt es nur in der update-view

        kwargs['feste_schichten_liste'] = get_feste_schichten(asn=self.request.user.asn, assistent=self.request.user)

        # alle schicht_templates des asn
        kwargs['schicht_template_liste'] = get_schicht_templates(self.request.user.asn)

        context = super(AsnEditAsView, self).get_context_data(**kwargs)

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

        feste_schicht = form['asn_feste_schicht'].save(commit=False)
        if int(feste_schicht.wochentag) > 0:
            feste_schicht.asn = asn
            feste_schicht.assistent = assistent
            feste_schicht.save()

        schicht_template = form['asn_schicht_templates'].save(commit=False)
        if schicht_template.bezeichner != '':
            schicht_template.asn = asn
            schicht_template.save()

        return redirect('asn_edit_as', pk=asn.id)


class DeleteFesteSchichtenView(LoginRequiredMixin, DeleteView):
    model = FesteSchicht
    success_url = reverse_lazy('create_as')


class DeleteSchichtTemplateView(LoginRequiredMixin, DeleteView):
    model = SchichtTemplate
    success_url = reverse_lazy('create_as')
