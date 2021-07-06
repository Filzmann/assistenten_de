from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from guardian.mixins import PermissionRequiredMixin
from guardian.shortcuts import assign_perm, get_objects_for_user

from assistenten.forms.edit_asn_multiform import EditAsnMultiForm, CreateAsnMultiForm
from assistenten.models import ASN, FesteSchicht, SchichtTemplate


class CreateAsnView(LoginRequiredMixin, CreateView):
    template_name = "assistenten/edit_asn.html"
    form_class = CreateAsnMultiForm
    model = ASN
    success_url = reverse_lazy('edit_asn')

    def get_context_data(self, **kwargs):
        asn_liste = []
        asns = get_objects_for_user(self.request.user, 'view_asn', klass=ASN, with_superuser=False)

        for asn in asns:
            asn_liste.append((asn.id, asn.kuerzel))
        kwargs['asn_liste'] = asn_liste
        context = super(CreateAsnView, self).get_context_data(**kwargs)
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

        return redirect('edit_asn', pk=asn.id)


class EditAsnView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    template_name = "assistenten/edit_asn.html"
    form_class = EditAsnMultiForm
    model = ASN
    success_url = reverse_lazy('edit_asn')
    permission_required = 'change_asn'

    def get_form_kwargs(self):
        kwargs = super(EditAsnView, self).get_form_kwargs()
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
        # alle festen Schichten des asn
        feste_schichten_liste = []
        feste_schichten = FesteSchicht.objects.filter(
            assistent=self.request.user.assistent.id).filter(
            asn=self.object.id)

        wtage = {'0': 'Mo', '1': 'Di', '2': 'Mi', '3': 'Do', '4': 'Fr', '5': 'Sa', '6': 'So'}

        for feste_schicht in feste_schichten:
            feste_schichten_liste.append({
                'id': feste_schicht.id,
                'wochentag': wtage[feste_schicht.wochentag],
                'beginn': feste_schicht.beginn.strftime("%H:%M"),
                'ende': feste_schicht.ende.strftime("%H:%M"),
            })
        kwargs['feste_schichten_liste'] = feste_schichten_liste
        # kwargs['feste_schichten_liste'] = ['bla', 'blubb', 'blu']

        # alle schicht_templates des asn
        schicht_template_liste = []
        schicht_templates = SchichtTemplate.objects.filter(
            asn=self.object.id)
        for schicht_template in schicht_templates:
            schicht_template_liste.append({
                'id': schicht_template.id,
                'bezeichner': schicht_template.bezeichner,
                'beginn': schicht_template.beginn.strftime("%H:%M"),
                'ende': schicht_template.ende.strftime("%H:%M"),
            })
        kwargs['schicht_template_liste'] = schicht_template_liste

        context = super(EditAsnView, self).get_context_data(**kwargs)

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

        return redirect('edit_asn', pk=asn.id)


class DeleteFesteSchichtenView(LoginRequiredMixin, DeleteView):
    model = FesteSchicht
    success_url = reverse_lazy('create_asn')


class DeleteSchichtTemplateView(LoginRequiredMixin, DeleteView):
    model = SchichtTemplate
    success_url = reverse_lazy('create_asn')
