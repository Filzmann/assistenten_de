from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from guardian.mixins import PermissionRequiredMixin
from guardian.shortcuts import assign_perm, get_objects_for_user

from assistenten.forms.assistent.as_edit_asn_multiform import AsEditAsnMultiForm, AsCreateAsnMultiForm
from assistenten.models import ASN, FesteSchicht, SchichtTemplate


class AsCreateAsnView(LoginRequiredMixin, CreateView):
    template_name = "assistenten/assistenten/as_edit_asn.html"
    form_class = AsCreateAsnMultiForm
    model = ASN
    success_url = reverse_lazy('as_edit_asn')

    def get_context_data(self, **kwargs):
        asn_liste = []
        asns = get_objects_for_user(self.request.user, 'view_asn', klass=ASN, with_superuser=False)

        for asn in asns:
            asn_liste.append((asn.id, asn.kuerzel))
        kwargs['asn_liste'] = asn_liste
        context = super(AsCreateAsnView, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        asn = form['asn_stammdaten'].save()
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


class AsEditAsnView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    template_name = "assistenten/assistenten/as_edit_asn.html"
    form_class = AsEditAsnMultiForm
    model = ASN
    success_url = reverse_lazy('as_edit_asn')
    permission_required = 'change_asn'

    def get_form_kwargs(self):
        kwargs = super(AsEditAsnView, self).get_form_kwargs()
        kwargs.update(instance={
            'asn_stammdaten': self.object,
            'asn_adresse': self.object.adressen.all().filter(is_home=True)[0]
        })
        return kwargs

    # For Update
    def get_context_data(self, **kwargs):

        # alle asn zur auswahl auflisten
        asn_liste = []
        asns = get_objects_for_user(self.request.user, 'change_asn', klass=ASN, with_superuser=False)
        for asn in asns:
            asn_liste.append((asn.id, asn.kuerzel))
        kwargs['asn_liste'] = asn_liste
        # feste schichten und templates gibt es nur in der update-view
        kwargs['feste_schichten_liste'] = FesteSchicht.get_list(asn=self.object, assistent=self.request.user.assistent)
        # alle schicht_templates des asn
        kwargs['schicht_template_liste'] = self.object.schicht_templates()

        context = super(AsEditAsnView, self).get_context_data(**kwargs)
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

        return redirect('as_edit_asn', pk=asn.id)


class DeleteFesteSchichtenView(LoginRequiredMixin, DeleteView):
    model = FesteSchicht
    success_url = reverse_lazy('as_create_asn')

    def get_success_url(self):

        assistent = self.object.assistent

        success_url = super(DeleteFesteSchichtenView, self).get_success_url()
        usergroup = self.request.user.groups.values_list('name', flat=True).first()
        if usergroup == "Assistenten":
            return reverse_lazy('as_create_asn')
        elif usergroup == "Assistenznehmer":
            return reverse_lazy('asn_edit_as', kwargs={'pk': assistent.id})


class DeleteSchichtTemplateView(LoginRequiredMixin, DeleteView):
    model = SchichtTemplate
    success_url = reverse_lazy('as_create_asn')

    def get_success_url(self):
        success_url = super(DeleteSchichtTemplateView, self).get_success_url()
        usergroup = self.request.user.groups.values_list('name', flat=True).first()
        if usergroup == "Assistenten":
            return reverse_lazy('as_create_asn')
        elif usergroup == "Assistenznehmer":
            return reverse_lazy('asn_edit_asn', kwargs={'pk': self.request.user.assistenznehmer.id})
