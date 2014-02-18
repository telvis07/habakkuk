__author__ = 'telvis'

from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
import logging
from mock import patch, MagicMock
logger = logging.getLogger(__name__)

class ViewsTest(TestCase):
    ES_SETTINGS = {
        'hosts':['nosuchhost:9200'],
        'search_index':'nosuch-index-*',
        'model_index':'nosuch-index-*',
    }

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @override_settings(ES_SETTINGS=ES_SETTINGS)
    def test_default_redirect(self):
        """ should redirect to clusters """
        mock_es_conn = MagicMock()
        with patch('web.search.get_es_connection', return_value=mock_es_conn):
            client = Client()
            response = client.get("/")
            self.assertEquals(301, response.status_code)

            # verify I still get data after the redirect
            response = client.get("/", follow=True)
            self.assertEquals([('http://testserver/biblestudy/', 301)], response.redirect_chain)
            self.assertEquals(200, response.status_code)

    @override_settings(ES_SETTINGS=ES_SETTINGS)
    def test_bible_study_view(self):
        """ test the bible study view """
        mock_es_conn = MagicMock()
        with patch('web.search.get_es_connection', return_value=mock_es_conn):
            client = Client()
            response = client.get("/biblestudy/")
            self.assertEquals(200, response.status_code)