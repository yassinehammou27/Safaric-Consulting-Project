from django.test import SimpleTestCase
from django.urls import reverse, resolve
from auswertung.views import (home,
                            HandzettelListView,
                            ausw_HandzettelListView,
                            handzettelAuswertung,
                            seiteAuswertung,
                            artikelAuswertung,
                            )

class TestUrls(SimpleTestCase):

    def test_home_url_resolves(self):
        url = reverse('auswertung-home')
        self.assertEqual(resolve(url).func, home)

    def test_handzettelliste_url_resolves(self):
        url = reverse('auswertung-handzettelliste')
        self.assertEqual(resolve(url).func.view_class, HandzettelListView)

    def test_ausw_handzettelliste_url_resolves(self):
        url = reverse('auswertung-ausw_handzettelliste')
        self.assertEqual(resolve(url).func.view_class, ausw_HandzettelListView)
    
    def test_handzettelauswertung_url_resolves(self):
        url = reverse('auswertung-handzettel', args=['1'])
        self.assertEqual(resolve(url).func.__name__, handzettelAuswertung.__name__)

    def test_seitenauswertung_url_resolves(self):
       url = reverse('auswertung-seite', args=['1', '1'])
       self.assertEqual(resolve(url).func.__name__, seiteAuswertung.__name__)

    def test_artikelauswertung_url_resolves(self):
       url = reverse('auswertung-artikel')
       self.assertEqual(resolve(url).func.__name__, artikelAuswertung.__name__)

