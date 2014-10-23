__author__ = 'telvis'

from django.test import TestCase
from django.test.utils import override_settings
from mock import DEFAULT, patch, MagicMock
import numpy as np

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