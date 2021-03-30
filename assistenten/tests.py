from django.http import HttpRequest
from django.test import TestCase
from django.urls import resolve
from assistenten.views import index


class IndexPageTest(TestCase):

# Create your tests here.

    def test_root_url_resolves_to_assistent_index(self):
        found = resolve("/")
        self.assertEqual(found.func, index)

    def test_home_page_returns_correct_html(self):
        request = HttpRequest()
        response = index(request)
        html = response.content.decode('utf8')
        self.assertTrue(html.strip().startswith('<!doctype html>'))
        self.assertIn('<title>Assistenten - Dashboard</title>', html)
        self.assertTrue(html.strip().endswith('</html>'))


