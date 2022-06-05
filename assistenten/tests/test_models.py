from django.utils import timezone

from django.test import TestCase
from django.utils.datetime_safe import datetime

from assistenten.models import AbstractZeitraum


class AbstractZeitraumModelTest(TestCase):
    def test_abstract_zeitraum_check_mehrtaegig(self):
        zeitraum = AbstractZeitraum()
        zeitraum.beginn = timezone.make_aware(datetime(2021,12,31,22,0))
        zeitraum.ende = timezone.make_aware(datetime(2022, 1, 2, 22, 0))
        print(zeitraum)
        result = zeitraum.split_by_null_uhr()
        self.assertTrue(len(result), 3)

# Create your tests here.
