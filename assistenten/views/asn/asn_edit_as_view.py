from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, CreateView
from guardian.mixins import PermissionRequiredMixin
from guardian.shortcuts import assign_perm, get_objects_for_user

from assistenten.forms.asn.asn_edit_as_multiform import AsnCreateAsMultiForm, AsnEditAsMultiForm
from assistenten.models import Assistent, FesteSchicht


class AsnCreateAsView(LoginRequiredMixin, CreateView):
    template_name = "assistenten/asn/asn_edit_as.html"
    form_class = AsnCreateAsMultiForm
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
        user = self.request.user
        asn = user.assistenznehmer
        assistent = form['as_stammdaten'].save()
        asn.assistents.add(assistent)
        asn.save()
        adresse = form['asn_adresse'].save(commit=False)
        adresse.asn = asn
        adresse.is_home = True
        adresse.save()
        # der eingeloggte user erhält das Bearbeitungsrecht
        assign_perm('change_assistent', user, assistent)
        assign_perm("view_assistent", user, assistent)

        return redirect('asn_edit_as', pk=assistent.id)


class AsnEditAsView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    template_name = "assistenten/asn/asn_edit_as.html"
    form_class = AsnEditAsMultiForm
    model = Assistent
    success_url = reverse_lazy('asn_edit_as')
    permission_required = 'view_assistent'

    def get_form_kwargs(self):
        kwargs = super(AsnEditAsView, self).get_form_kwargs()
        kwargs.update(instance={
            'as_stammdaten': self.object,
            'as_adresse': self.object.adressen.all().filter(is_home=True)[0]
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

        kwargs['feste_schichten_liste'] = FesteSchicht.get_list(
            asn=self.request.user.assistenznehmer, assistent=self.object)

        context = super(AsnEditAsView, self).get_context_data(**kwargs)

        return context

    def form_valid(self, form):
        assistent = form['as_stammdaten'].save()
        asn = self.request.user.assistenznehmer
        asn.assistents.add(assistent)
        asn.save()
        adresse = form['as_adresse'].save(commit=False)
        adresse.asn = asn
        adresse.is_home = True
        adresse.save()

        feste_schicht = form['as_feste_schicht'].save(commit=False)

        if int(feste_schicht.wochentag) > 0:
            feste_schicht.asn = asn
            feste_schicht.assistent = assistent
            feste_schicht.save()

        return redirect('asn_edit_as', pk=assistent.id)
