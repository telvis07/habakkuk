__author__ = 'telvis'
from django.test import TestCase
from django.test.utils import override_settings
from mock import patch, MagicMock, call
import logging
import json

from web.search import get_scriptures_by_date, bibleverse_facet
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
        """ test the func that performs the ES search """
        bv = {"bibleverse":"1 John 4:19"}
        text = {"bibleverse":"1 John 4:19", "text": "We love because he first loved us."}
        recommendations = {"bibleverse":"1 John 4:19", "text": "We love because he first loved us.",
                                "recommendations":["Book 2:1", "Book 2:2", "Book 2:3"]}

        with patch('web.search.bibleverse_facet',return_value=bv) as mock_facet_search:
         with patch('web.search.bibleverse_text', return_value=text) as mock_text:
          with patch("web.search.bibleverse_recommendations", return_value=recommendations) as mock_rec:
            ret = get_scriptures_by_date(size=5)

        self.assertTrue(mock_facet_search.called)
        mock_facet_search.assert_called_with(host=['nosuchhost:9200'],
                                             index='nosuch-index-*',
                                             start=None,
                                             end=None,
                                             _date=None,
                                             size=5)
        mock_text.assert_called_with(bv)
        mock_rec.assert_called_with(text)
        self.assertEquals(recommendations, ret)

    @override_settings(ES_SETTINGS=ES_SETTINGS)
    def test_bibleverse_facet(self):
        """test faceted search to ES using pyes"""

        hosts = self.ES_SETTINGS['hosts']
        search_index = self.ES_SETTINGS['search_index']
        mock_es_conn = MagicMock()
        with patch('web.search.get_es_connection', return_value=mock_es_conn) as mock_get_conn:
            mock_result_set = MagicMock()
            mock_result_set.facets = {'bibleverse':
                                          {'total': 1,
                                           'terms':[
                                               {'term':'i_john', 'count':1}
                                           ]
                                          }
                                       }
            mock_es_conn.search.return_value = mock_result_set
            ret = bibleverse_facet(host=hosts, index=search_index, start=None, end=None, size=5)
        mock_get_conn.assert_called_with(['nosuchhost:9200'])
        self.assertTrue(mock_es_conn.search.called)
        self.assertEquals([{'bibleverse':'i_john'}], ret)

    @override_settings(ES_SETTINGS=ES_SETTINGS)
    def test_bibleverse_facet_range(self):
        """test faceted search to ES using pyes with various range options"""
        expected_calls = [
                          # 1. call with only start date
                          call(indices='nosuch-index-*-*', doc_types=['habakkuk'], query={'query': {
                           'filtered': {'filter': {'range': {'created_at_date': {'from': '2013-01-01', 'include_lower': True}}},
                           'query': {'match_all': {}}}}, 'facets': {
                           'bibleverse': {'terms': {'field': 'bibleverse', 'order': 'count', 'size': 10}}}, 'size': 0}),
                          # 2. call with only end date
                          call(indices='nosuch-index-*-*', doc_types=['habakkuk'], query={'query': {'filtered': {
                           'filter': {'range': {'created_at_date': {'to': '2013-01-01', 'include_upper': True}}},
                           'query': {'match_all': {}}}}, 'facets': {
                           'bibleverse': {'terms': {'field': 'bibleverse', 'order': 'count', 'size': 10}}}, 'size': 0}),
                          # 3. call with only date
                          call(indices='nosuch-index-*-*', doc_types=['habakkuk'], query={'query': {
                           'filtered': {'filter': {'term': {'created_at_date': '2013-01-01'}},
                                       'query': {'match_all': {}}}}, 'facets': {
                           'bibleverse': {'terms': {'field': 'bibleverse', 'order': 'count', 'size': 10}}}, 'size': 0}),
                          # 4. call with start and end date
                          call(indices='nosuch-index-*-*', doc_types=['habakkuk'], query={'query': {'filtered': {
                           'filter': {'range': {
                           'created_at_date': {'to': '2013-01-02', 'include_upper': False, 'from': '2013-01-01'}}},
                           'query': {'match_all': {}}}}, 'facets': {
                           'bibleverse': {'terms': {'field': 'bibleverse', 'order': 'count', 'size': 10}}}, 'size': 0})]

        hosts = self.ES_SETTINGS['hosts']
        search_index = self.ES_SETTINGS['search_index']
        mock_es_conn = MagicMock()
        with patch('web.search.get_es_connection', return_value=mock_es_conn) as mock_get_conn:
            mock_result_set = MagicMock()
            mock_result_set.facets = {'bibleverse':
                                          {'total': 1,
                                           'terms':[
                                               {'term':'i_john', 'count':1}
                                           ]
                                          }
                                       }
            mock_es_conn.search.return_value = mock_result_set
            kwarg_list = [
                {'host':hosts, 'index':search_index, 'start':'2013-01-01'},
                {'host':hosts, 'index':search_index, 'end':'2013-01-01'},
                {'host':hosts, 'index':search_index, '_date':'2013-01-01'},
                {'host':hosts, 'index':search_index, 'start':'2013-01-01', 'end':'2013-01-02'},
            ]

            # call bibleverse_facet with all the keyword args
            for kwargs in kwarg_list:
                bibleverse_facet(**kwargs)

        i=0
        for expected_call, actual_call in zip(expected_calls, mock_es_conn.search.mock_calls):
            name, args, kwargs = actual_call
            ex_name, ex_args, ex_kwargs = expected_call
            self.assertEquals(ex_kwargs['query'], kwargs['query'].serialize())
            i+=1
