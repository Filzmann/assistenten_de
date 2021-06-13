from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView

from assistenten.models import Schicht


class AskholeView(LoginRequiredMixin, TemplateView):
    model = Schicht
    context_object_name = 'askhole'
    template_name = 'assistenten/askhole.html'
    act_date = timezone.now()
