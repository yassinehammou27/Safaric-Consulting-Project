from django.test import TestCase, Client
from django.urls import reverse 
from auswertung.models import Handzettel, Haendler, Seite, CustomUser, ArtikelDictionary, KategorieArtikel, Unternehmensgruppe, Branche
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile

class TestViews(TestCase):

    def setUp(self):
        user = CustomUser.objects.create_superuser('testuser','test@mail.de','secret')
        user.save()
        self.client = Client()
        self.handzettel_pdf = BytesIO(b'mybinarydata')
        self.handzettel_pdf.name = 'Aldi_11_2020.pdf'
        #self.seite_img = BytesIO(b'mybinarydata')
        #self.seite_img.name = 'Aldi_11_2020.img'
        self.branche_object = Branche.objects.create(
            name = 'LEH'
        )
        self.unternehmensgruppe_object = Unternehmensgruppe.objects.create(
            name = 'Schwarzgruppe',
            branche = self.branche_object
        )
        self.haendler_objekt = Haendler.objects.create(
            name = 'Aldi',
            branche = self.branche_object,
            unternehmensgruppe = self.unternehmensgruppe_object
        )
        self.handzettel_objekt = Handzettel.objects.create(
            haendler = self.haendler_objekt,
            jahr = '2020',
            # start = '2020-01-01',
            # ende = '2020-01-01',
            seitenanzahl = 1,
            kw = 1,
            handzetteldatei = SimpleUploadedFile("test.txt", b"test")
        )
        self.seiten_objekt = Seite.objects.create(
            handzettel = self.handzettel_objekt,
            seitenzahl = 1,
        )
        self.kategorie_object = KategorieArtikel.objects.create(
            name = "Testkategorie"
        )
        self.artikeldictionary_object = ArtikelDictionary.objects.create(
            key = self.kategorie_object
        )
        self.handzettelliste_url = reverse('auswertung-handzettelliste')
        self.home_url = reverse('auswertung-home')
        self.ergebnisse_url = reverse('auswertung-ergebnisse')
        self.seite_url = reverse('auswertung-seite', args=['1','1'])
        self.artikel_url = reverse('auswertung-artikel')
        self.upload_url = reverse('uploadstart')
        self.ausw_handzettelliste_url = reverse('auswertung-ausw_handzettelliste')

    def test_home_GET(self):
        self.client.login(username = 'testuser', password = 'secret')
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auswertung/home.html')


    def test_handzettel_list_GET(self):
        self.client.login(username = 'testuser', password = 'secret')
        response = self.client.get(self.handzettelliste_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auswertung/handzettelliste.html')

    def test_ausw_handzettel_list_GET(self):
        self.client.login(username = 'testuser', password = 'secret')
        response = self.client.get('/auswertung/ausw_handzettelliste/') 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auswertung/ausw_handzettelliste.html')

    def test_handzettel_list_GET_ohne_login(self):
        response = self.client.get(self.handzettelliste_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auswertung/403.html')

    def test_home_GET_ohne_login(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 302)


    def test_seite_GET_ohne_login(self):
        response = self.client.get(self.seite_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auswertung/403.html')

    def test_artikel_GET_ohne_login(self):
        response = self.client.get(self.artikel_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auswertung/403.html')

#     def test_upload_GET_ohne_login(self):
#         response = self.client.get(self.upload_url)
#         self.assertEqual(response.status_code, 302)

    def test_ausw_handzettelliste_GET_ohne_login(self):
        response = self.client.get(self.ausw_handzettelliste_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auswertung/403.html')
