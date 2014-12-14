__author__ = 'telvis'

from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
import logging
from mock import patch, MagicMock
logger = logging.getLogger(__name__)
import jsonlib2 as json

class ViewsTest(TestCase):
    ES_SETTINGS = {
        'hosts':['nosuchhost:9200'],
        'search_index':'nosuch-index-*',
        'topics_index' : 'nosuch-index-*',
        'search_es_type' : 'habakkuk',
        'clusters_es_type' : 'topic_clusters',
        'phrases_es_type' : 'ranked_phrases'
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
            self.assertEquals([('http://testserver/topics/', 301)], response.redirect_chain)
            self.assertEquals(200, response.status_code)

    @override_settings(ES_SETTINGS=ES_SETTINGS)
    def test_bible_study_view(self):
        """ test the bible study view """
        mock_es_conn = MagicMock()
        with patch('web.search.get_es_connection', return_value=mock_es_conn):
            client = Client()
            response = client.get("/biblestudy/")
            self.assertEquals(200, response.status_code)

    @override_settings(ES_SETTINGS=ES_SETTINGS)
    def test_topics_view(self):
        mock_return =  {
            'count': 5,
            'topics' : [
                {
                    "bibleverse" : "luke 6:27",
                    "phrases" : [
                        {
                            "es_phrase": "love your enemies, do good to those who hate you",
                            "bibleverse": "luke 6:27",
                            "search_url" : "http://localhost:8000/biblestudy/?search=enemies+good"
                        }
                    ]
                },
                {
                    "bibleverse": "matthew 6:34",
                    "phrases" : [
                        {
                            "es_phrase": "don\u2019t worry about tomorrow",
                            "bibleverse" : "matthew 6:34",
                            "search_url" : "http://localhost:8000/biblestudy/?search=worry+tomorrow"
                        }
                    ]
                },
                {
                    "bibleverse" : "matthew 8:8",
                    "phrases" : [{
                        "es_phrase": "some more text",
                        "bibleverse" : "matthew 8:8",
                        "search_url" : "http://localhost:8000/biblestudy/?search=worry+tomorrow"
                    }],

                }
            ]
        }

        with patch('web.views.get_topics', return_value=mock_return) as mock_get_topics:
            client = Client()
            response = client.get('/topics/')
            self.assertEquals(200, response.status_code)
            self.assertTrue(response.context["topic_results"])
            self.assertTrue(response.context['topic_results'].get('count'))
            self.assertTrue(response.context['topic_results'].get('topics'))
            self.assertTrue(mock_get_topics.called)

    @override_settings(ES_SETTINGS=ES_SETTINGS)
    def test_topics_api_view(self):
        mock_return =  {
            'count': 5,
            'topics' : [
                {
                    "bibleverse" : "luke 6:27",
                    "phrases" : [
                        {
                            "es_phrase": "love your enemies, do good to those who hate you",
                            "bibleverse": "luke 6:27",
                            "search_url" : "http://localhost:8000/biblestudy/?search=enemies+good"
                        }
                    ]
                },
                {
                    "bibleverse": "matthew 6:34",
                    "phrases" : [
                        {
                            "es_phrase": "don\u2019t worry about tomorrow",
                            "bibleverse" : "matthew 6:34",
                            "search_url" : "http://localhost:8000/biblestudy/?search=worry+tomorrow"
                        }
                    ]
                },
                {
                    "bibleverse" : "matthew 8:8",
                    "phrases" : [{
                        "es_phrase": "some more text",
                        "bibleverse" : "matthew 8:8",
                        "search_url" : "http://localhost:8000/biblestudy/?search=worry+tomorrow"
                    }],

                }
            ]
        }

        with patch('web.views.get_topics', return_value=mock_return) as mock_get_topics:
            client = Client()
            response = client.post('/api/topics/',
                                   content_type="application/json",
                                   data=json.dumps({'size':10, 'offset': 99}))
            try:
                ret = json.loads(response.content)
            except:
                self.fail("Could not parse the response from topics_api \n{}".format(response.content))

            self.assertEquals(200, response.status_code)
            self.assertTrue(ret["topic_results"])
            self.assertTrue(ret['topic_results'].get('count'))
            self.assertTrue(ret['topic_results'].get('topics'))
            self.assertEquals(99, ret['offset'])
            self.assertTrue(mock_get_topics.called)


    @override_settings(ES_SETTINGS=ES_SETTINGS)
    def test_topics_api_view_no_data(self):
        # """
        # verify we get a 200 OK even if we don't send POST data
        # :return:
        # """
        mock_return =  {
            'count': 5,
            'topics' : [
                {
                    "es_phrase": "love your enemies, do good to those who hate you",
                    "bibleverse": "luke 6:27",
                    "search_url" : "http://localhost:8000/biblestudy/?search=enemies+good"
                },
                {
                    "es_phrase": "don\u2019t worry about tomorrow",
                    "bibleverse" : "matthew 6:34",
                    "search_url" : "http://localhost:8000/biblestudy/?search=worry+tomorrow"
                },
                {
                    "es_phrase": "some more text",
                    "bibleverse" : "matthew 8:8",
                    "search_url" : "http://localhost:8000/biblestudy/?search=worry+tomorrow"
                }
            ]
        }

        with patch('web.views.get_topics', return_value=mock_return) as mock_get_topics:
            client = Client()
            response = client.post('/api/topics/')
            try:
                ret = json.loads(response.content)
            except:
                self.fail("Could not parse the response from topics_api \n{}".format(response.content))
            self.assertEquals(200, response.status_code)


