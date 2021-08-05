from guardian.shortcuts import get_objects_for_user
from assistenten.models import ASN
from assistenten.views.abstract_dienstplan_view import AbstractDienstplanView


class EbDienstplanView(AbstractDienstplanView):
    context_object_name = 'eb_dienstplan_monat'
    template_name = 'assistenten/ebs/show_dienstplan.html'

    def get_context_data(self, **kwargs):
        if 'asn_id' in kwargs:
            self.asn = ASN.objects.get(pk=kwargs['asn_id'])
        context = super(EbDienstplanView, self).get_context_data(**kwargs)

        asn_liste = []
        asns = get_objects_for_user(self.request.user, 'view_asn', klass=ASN, with_superuser=False)
        for asn in asns:
            asn_liste.append((asn.id, asn.kuerzel))
        context['asn_liste'] = asn_liste
        self.reset()
        return context
