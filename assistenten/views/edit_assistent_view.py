from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.edit import FormView, UpdateView

from assistenten.models import Assistent
from assistenten.forms import EditAsForm


class EditAssistentView(UpdateView):
    template_name = "assistenten/edit_assistent.html"
    form_class = EditAsForm
    model = Assistent


    def get_name(request):
        # if this is a POST request we need to process the form data
        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            form = EditAsForm(request.POST)
            # check whether it's valid:
            if form.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:
                return HttpResponseRedirect('/thanks/')

        # if a GET (or any other method) we'll create a blank form
        else:
            form = EditAsForm()

        return render(request, 'name.html', {'form': form})