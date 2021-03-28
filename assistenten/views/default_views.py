from django.http import HttpResponse
from django.template import loader
from assistenten.models import Lohn


def index(request):

    lohn_list = Lohn.objects.all()
    print(lohn_list)
    template = loader.get_template('assistenten/index.html')
    context = {
        'lohn_list': lohn_list,
    }
    return HttpResponse(template.render(context, request))
