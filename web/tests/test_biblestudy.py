__author__ = 'telvis'
from django.test import TestCase
from django.test.utils import override_settings
from mock import patch, MagicMock, call, DEFAULT
import logging
from web.models import BibleText

from web.search import get_scriptures_by_date, bibleverse_facet, bibleverse_text
logger = logging.getLogger(__name__)

class BibleStudyTest(TestCase):
    ES_SETTINGS = {
        'hosts':['nosuchhost:9200'],
        'search_index':'nosuch-index-*',
        'model_index':'nosuch-index-*',
    }

    def setUp(self):
        self.bt_entries = [{'bibleverse':'the-verse 1:1',
                            'bibleverse_human':'The Verse 1:1',
                            'text':"text 1:1",
                            'translation': 'KJV'},
                           {'bibleverse':'the-verse 1:2',
                            'bibleverse_human':'The Verse 1:2',
                            'text':"text 1:2",
                            'translation': 'KJV'}]
        translation = 'KJV'
        for i, bv in enumerate(self.bt_entries):
            bibleverse = bv['bibleverse']
            text = bv['text']
            BibleText.objects.get_or_create(verse_id=i, translation=translation,
                                            bibleverse_human=bv['bibleverse_human'],
                                            defaults={'bibleverse':bibleverse,
                                                      'text':text})

    def tearDown(self):
        for bt in BibleText.objects.all():
            bt.delete()

    @override_settings(ES_SETTINGS=ES_SETTINGS)
    def test_get_scriptures_by_date(self):
        """ test the func that performs the ES search """
        bv = {"bibleverse":"1 John 4:19"}
        text = {"bibleverse":"1 John 4:19", "text": "We love because he first loved us."}
        recommendations = {"bibleverse":"1 John 4:19", "text": "We love because he first loved us.",
                                "recommendations":["Book 2:1", "Book 2:2", "Book 2:3"]}

        patches = {
            'bibleverse_facet' : MagicMock(return_value=bv),
            'bibleverse_text' : MagicMock(return_value=text),
            'bibleverse_recommendations' : MagicMock(return_value=recommendations)
        }

        with patch.multiple('web.search', ** patches):
            mock_facet_search = patches['bibleverse_facet']
            mock_text = patches['bibleverse_text']
            mock_rec = patches['bibleverse_recommendations']
            ret = get_scriptures_by_date(size=5)

            self.assertTrue(mock_facet_search.called)
            mock_facet_search.assert_called_with(host=['nosuchhost:9200'],
                                                 index='nosuch-index-*',
                                                 start=None,
                                                 end=None,
                                                 _date=None,
                                                 size=5,
                                                 search_text=None)
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

    @override_settings(ES_SETTINGS=ES_SETTINGS)
    def test_bibleverse_text(self):
        """
        test BibleText Model lookups
        """

        no_such_verse = 'no-such-verse 1:1'
        entries = [{'bibleverse':'the-verse 1:1'},
                   {'bibleverse':'the-verse 1:2'},
                   {'bibleverse':no_such_verse}]
        ret = bibleverse_text(entries)

        # verify it returns the BibleText entries loaded in setUp()
        # should contains bibleverse_human entries
        self.assertEquals(self.bt_entries, ret)

        # verify it does not return 'no-such-verse'
        ret = filter(lambda x: x['bibleverse'] == no_such_verse, ret)
        self.assertEquals(0, len(ret))
