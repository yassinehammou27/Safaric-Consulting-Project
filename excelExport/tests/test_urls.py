from django.test import SimpleTestCase
from django.urls import reverse, resolve
from excelExport.views import ergebnisse

class TestUrls(SimpleTestCase):

    def test_ergebnisse_url_resolves(self):
        url = reverse('auswertung-ergebnisse')
        self.assertEqual(resolve(url).func.__name__, ergebnisse.__name__)