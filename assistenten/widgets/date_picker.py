from django.forms import DateInput


class XDSoftDatePickerInput(DateInput):
    """
    widget to show the datetimepicker from this tutorial
    contains 3 Widgets:
    - date_picker
    - datetime_picker
    - time_picker
    https://xdsoft.net/jqplugins/datetimepicker/

    Tutorial:
    https://simpleisbetterthancomplex.com/tutorial/2019/01/03/how-to-use-date-picker-with-django.html
    """
    template_name = 'widgets/xdsoft_date_picker.html'
