from django.http import HttpRequest
from django.test import TestCase
from django.urls import resolve
from assistenten.views.hilfe_view import HilfeView


class IndexPageTest(TestCase):

    # Create your tests here.

    def test_root_url_resolves_to_assistent_index(self):
        found = resolve("/")
        # self.assertEqual(found.func, HilfeView)
