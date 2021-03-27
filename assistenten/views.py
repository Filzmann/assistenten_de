from django.http import HttpResponse
from django.template import loader
from .models import Lohn


def index(request):
    latest_lohn_list = Lohn.objects.order_by('-id')[:5]
    template = loader.get_template('assistenten/index.html')
    context = {
        'latest_question_list': latest_lohn_list,
    }
    return HttpResponse(template.render(context, request))


def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % question_id)


def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)


def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)
