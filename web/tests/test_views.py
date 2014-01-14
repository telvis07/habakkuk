__author__ = 'telvis'

from django.test import TestCase
from django.test.client import Client
import logging
logger = logging.getLogger(__name__)

class ViewsTest(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_default_redirect(self):
        """ should redirect to clusters """
        client = Client()
        response = client.get("/")
        self.assertEquals(301, response.status_code)

        # verify I still get data after the redirect
        response = client.get("/", follow=True)
        self.assertEquals([('http://testserver/biblestudy/', 301)], response.redirect_chain)
        self.assertEquals(200, response.status_code)

    def test_bible_study_view(self):
        """ test the bible study view """
        client = Client()
        response = client.get("/biblestudy/")
        self.assertEquals(200, response.status_code)