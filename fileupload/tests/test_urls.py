from django.test import SimpleTestCase
from django.urls import reverse, resolve
from fileupload.views import upload_handout

class TestUrls(SimpleTestCase):
    
    def test_uploadhandzettel_url_resolves(self):
        url = reverse('uploadstart')
        self.assertEqual(resolve(url).func.__name__, upload_handout.__name__)