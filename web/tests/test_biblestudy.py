__author__ = 'telvis'
from django.test import TestCase
from django.test.utils import override_settings
from mock import patch
import logging

from web.search import get_scriptures_by_date
logger = logging.getLogger(__name__)

class BibleStudyTest(TestCase):
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
    def test_get_scriptures_by_date(self):
        """ test the bible study view """
        bv = {"bibleverse":"1 John 4:19", "count":1}
        text = {"bibleverse":"1 John 4:19", "count":1, "text": "We love because he first loved us."}
        recommendations = {"bibleverse":"1 John 4:19", "count":1, "text": "We love because he first loved us.",
                                "recommendations":["Book 2:1", "Book 2:2", "Book 2:3"]}

        with patch('web.search.bibleverse_facet',return_value=bv) as mock_facet_search:
         with patch('web.search.bibleverse_text', return_value=text) as mock_text:
          with patch("web.search.bibleverse_recommendations", return_value=recommendations) as mock_rec:
            ret = get_scriptures_by_date(live_hack=False, size=5)

        self.assertTrue(mock_facet_search.called)
        mock_facet_search.assert_called_with(host=['nosuchhost:9200'],
                                             index='nosuch-index-*',
                                             start=None,
                                             end=None,
                                             size=5)
        mock_text.assert_called_with(bv)
        mock_rec.assert_called_with(text)
        self.assertEquals(recommendations, ret)

