from django.forms import DateTimeInput


class DateTimePickerInput(DateTimeInput):
    template_name = 'widgets/datetime_picker.html'
