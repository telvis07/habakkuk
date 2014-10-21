__author__ = 'telvis'

from django.test import TestCase
from datetime import datetime, timedelta
from django.test.utils import override_settings
from collections import Counter
from mock import patch, MagicMock
from pandas import DataFrame
import logging

from topic_analysis import clustering

logger = logging.getLogger(__name__)

class ClusteringTest(TestCase):
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
    def test_get_data_from_store(self):
        """
        Verify we get facets and counts
        :return:
        """
        st = datetime(year=2014,month=1,day=1)
        et = datetime(year=2014,month=1,day=8)
        valid_bv_set = set(['genesis 1:1'])

        with patch('topic_analysis.clustering.search.bibleverse_facet') as mock_hk_facet:
            mock_hk_facet.return_value = [{'bibleverse':'genesis 1:1', 'count':1}]
            offset = 0
            for ret in clustering.get_data_from_store(st,et,valid_bv_set=valid_bv_set):
                expected = (st+timedelta(days=offset), Counter({'genesis 1:1': 1}))
                self.assertEquals(expected, ret)
                offset+=1

    @override_settings(ES_SETTINGS=ES_SETTINGS)
    def test_get_most_common_df(self):
        """
        verify we get a dataframe from the containing the items
        with 3 largest counts

        :return:
        """
        data = {
            '2014-01-01':Counter({'john 3:16':10,
                                  'philipians 4:13':9,
                                  'genesis 1:1':8,
                                  'habakkuk 1:1':7})
        }
        df = clustering.get_most_common_df(data)
        self.assertIsInstance(df, DataFrame)
        self.assertEquals((3,1), df.shape)


    def test_get_count_features_df(self):
        """
        verify returns velocity features for the dataframe
        :return:
        """
        data = {
            '2014-01-01':{'john 3:16':10,
                          'philipians 4:13':9,
                           'genesis 1:1':8,
                           'habakkuk 1:1':7}
        }
        test_input = DataFrame(data)
        ret = clustering.get_count_features_df(test_input)
        self.assertEquals(['count_entries', 'max', 'count_entries_norm', 'max_norm'],
                          list(ret.columns.values))

    def test_build_clusters(self):
        """
        verify we return cluster data
        :return:
        """
        class mock_kmeans_ret:
            labels_ = ['1','2','3']
            cluster_centers_ = [(1,1),(2,2),(3,3)]

        with patch('topic_analysis.clustering.KMeans') as mock_kmeans:
            mock_kmeans_obj = MagicMock(return_value=mock_kmeans_ret)
            mock_kmeans.return_value = mock_kmeans_obj
            ret = clustering.build_clusters(MagicMock())
            self.assertEquals(['clusters', 'labels', 'cluster_centers'],
                              ret.keys())
            self.assertTrue(mock_kmeans_obj.fit_predict.called)




