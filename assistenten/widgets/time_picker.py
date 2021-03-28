from django.forms import TimeInput
from datetime import datetime, timedelta

from django.utils.safestring import mark_safe


class XDSoftTimePickerInput(TimeInput):
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
    template_name = 'widgets/xdsoft_time_picker.html'

    allowTimes = [(datetime(1, 1, 1, 0, 0) + timedelta(minutes=(x * 30))).strftime("'%H:%M'") for x in range(0, 48)]
    options = ', '.join(allowTimes)

    extra_widget_data = mark_safe('allowTimes: [' + options + '], \n')

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['custom_data'] = self.extra_widget_data
        return context
