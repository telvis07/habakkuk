__author__ = 'telvis'

from django.test import TestCase
from django.test.utils import override_settings
from mock import DEFAULT, patch, MagicMock
import numpy as np
from datetime import date
from django.conf import settings
import os
import jsonlib2 as json

from topic_analysis import topic_extraction


class TopicAnalysisTest(TestCase):
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
    def test_nmf_topic_extraction(self):
        """
        test topic extraction
        :return:
        """

        # mock TfidfVectorizer
        mock_vectorizer_inst = MagicMock()
        mock_vectorizer_inst.get_feature_names.return_value = ['test1', 'test2', 'test3']
        mock_vectorizer = MagicMock(return_value=mock_vectorizer_inst)

        # mock decomposition.NMF
        mock_NMF_inst = MagicMock()
        mock_NMF_inst.components_ = [np.array([0.10, 0.20, 0.30])]

        class MockNMF:
            def __init__(self, *args, **kwargs):
                pass

            def fit(self, *args, **kwargs):
                return mock_NMF_inst

        patches = {
            'TfidfVectorizer': mock_vectorizer,
            'TfidfTransformer' : DEFAULT,
            'NMF' : MockNMF
        }

        with patch.multiple('topic_analysis.topic_extraction', **patches) as mocks:
            ret = topic_extraction.nmf_topic_extraction(['test1', 'test2', 'test3', 'stopword1'],
                                                  ['stopword1','stopword2'])
            # 1 topic
            self.assertEquals(1, len(ret))
            topic = ret[0]

            # 3 topic terms
            self.assertEquals(3, len(topic))

            # verify the topic terms are sorted in descending order
            # by weight
            expected = [{'text': 'test3', 'weight': 0.30},
                        {'text': 'test2', 'weight': 0.20},
                        {'text': 'test1', 'weight': 0.10}]
            self.assertEquals(expected, topic)


    @override_settings(ES_SETTINGS=ES_SETTINGS)
    def test_get_text_from_es(self):
        """
        test code that retrieves tweets from ES. Verify 'entities' are removed
        :return:
        """
        mock_es_conn = MagicMock()
        patches = {
            'RangeFilter' : DEFAULT,
            'ESRange' : DEFAULT,
            'FilteredQuery' : DEFAULT,
            'MatchAllQuery' : DEFAULT,
            'ANDFilter' : DEFAULT,
            'get_es_connection' : MagicMock(return_value=mock_es_conn)
        }



        with patch.multiple('topic_analysis.topic_extraction', **patches) as mocks:
            mock_result_set = [
                {'text': "#hello @nurse sweet!"}
            ]
            mock_es_conn.search.return_value = mock_result_set
            ret = topic_extraction.get_text_from_es('john 3:16', date(2014, 01, 01), date(2014, 01, 07))
            self.assertEquals(['sweet!'], ret)

    def test_phrase_search(self):
        """
        moar tests
        """

        mock_es_conn = MagicMock()
        patches = {
            'RangeFilter' : DEFAULT,
            'ESRange' : DEFAULT,
            'FilteredQuery' : DEFAULT,
            'TermsFilter' : DEFAULT,
            'MatchAllQuery' : DEFAULT,
            'ANDFilter' : DEFAULT,
            'get_es_connection' : MagicMock(return_value=mock_es_conn)
        }

        my_dict = {'bibleverse' : 'test 1:1'}
        def getitem(name):
            return my_dict[name]

        def setitem(name, val):
            my_dict[name] = val

        with patch.multiple('topic_analysis.topic_extraction', **patches) as mocks:
            mock_es_doc = MagicMock()
            mock_es_doc.text = "love and awesome peace on earth! homey!"
            mock_es_doc._meta.score = 99
            mock_es_doc.__getitem__.side_effect = getitem
            mock_result_set = [
                mock_es_doc
            ]
            mock_es_conn.search.return_value = mock_result_set
            ret = topic_extraction.phrase_search([[{'text': 'love peace', 'weight' : 1}]],
                                                 ['john 3:16'],
                                                 date(2014, 01, 01),
                                                 date(2014, 01, 07))
            # num topics
            self.assertEquals(1, len(ret))
            ret = ret[0]
            # num topic terms
            self.assertEquals(1, len(ret))

            # phrase ret
            phrase_ret = ret[0]
            expected = {'weight': 1, 'text': 'love peace', 'es_score': 99, 'final_score': 99,
                        'bibleverse':'test 1:1',
                        'es_phrase': 'love and awesome peace on earth',
                        'tweet_text': 'love and awesome peace on earth! homey!'}
            self.assertEquals(expected, phrase_ret)


    def test_build_corpus(self):
        mock_result_set = [
                "foo", "bar", "baz"
        ]
        patches = {
            'get_text_from_es' : MagicMock(return_value=mock_result_set),
        }

        with patch.multiple('topic_analysis.topic_extraction', **patches):
            mock_get_text = patches['get_text_from_es']
            ret = topic_extraction.build_corpus(date(2014, 01, 01),
                                                date(2014, 01, 07),
                                                ['john 3:16'])
            expected = (['john', '3', '16'], ['foo bar baz'])
            self.assertEquals(expected, ret)

    def test_save_topic_clusters(self):
        mock_es_conn = MagicMock()
        patches = {
            'get_es_connection' : MagicMock(return_value=mock_es_conn)
        }

        with patch.multiple('topic_analysis.topic_extraction', **patches) as mocks:
            topic_extraction.save_topic_clusters({'cluster_topics' : {}})
            self.assertTrue(mock_es_conn.index.called)


    def test_rank_results(self):
        cluster_data = open(os.path.join(settings.PROJECT_ROOT,
                                         'topic_analysis',
                                         'testdata',
                                         'out.json')).read()
        cluster_data = json.loads(cluster_data)
        topic_extraction.rank_results(cluster_data)
