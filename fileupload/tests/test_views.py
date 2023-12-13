from django.test import TestCase, Client
from django.urls import reverse 
from auswertung.models import Handzettel, Haendler, Seite, CustomUser, Unternehmensgruppe, Branche
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
        self.upload_url = reverse('uploadstart')
       

    def test_upload_GET_ohne_login(self):
        response = self.client.get(self.upload_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auswertung/403.html')