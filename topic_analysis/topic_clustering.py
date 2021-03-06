__author__ = 'telvis'

from pandas import DataFrame, Series
from collections import Counter
from collections import defaultdict
from sklearn.cluster import KMeans
import json
from datetime import timedelta
import numpy

from web import search
from django.conf import settings

ES_SETTINGS = settings.ES_SETTINGS
hosts = ES_SETTINGS['hosts']
search_index = ES_SETTINGS['search_index']


def print_clusters(df, clusters):
    """
    get date, counter(bibleverse)

    :param df:
    :param clusters:
    :return:
    """
    for label in clusters:
        print "Cluster",label, json.dumps(clusters[label])
        print df.ix[clusters[label]][["count_entries", "max"]]


def get_data_from_store(st, et, valid_bv_set=set()):
    """
    faceted search to get COUNTs for bibleverses by date
    """

    _date = st
    while _date <= et:
        ret = search.bibleverse_facet(host=hosts,
                                      _date=_date.strftime("%Y-%m-%d"),
                                      with_counts=True)
        ret = filter(lambda x: x['bibleverse'] in valid_bv_set, ret)
        by_date_counter = Counter(dict([(x['bibleverse'], x['count']) for x in ret]))

        yield (_date, by_date_counter)
        _date += timedelta(days=1)


def get_most_common_df(data, num=3):
    """
    create a dictionary[date] = Series(3 top bibleverses per date)

    :param data:
    :param num:
    :return:
    """
    top_data = {}
    for created_at_date in data:
        _counter = data[created_at_date]
        top_data[created_at_date] = Series(dict(_counter.most_common(num)))
    return DataFrame(top_data)


def count_valid_entries(frame):
    return frame.count()

def get_count_features_df(df):
    # get bv counts and max counts
    df['count_entries'] = df.apply(count_valid_entries, axis=1)
    df['max'] = df.apply(numpy.max, axis=1)

    # get data frame with top info
    # normalize the max_count and max_value
    top_df = df[['count_entries', 'max']]
    top_df['count_entries_norm'] = top_df['count_entries']/top_df['count_entries'].max()
    top_df['max_norm'] = top_df['max']/top_df['max'].max()
    return top_df


def build_clusters(df, n_clusters=4):
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit_predict(df[['count_entries_norm', 'max_norm']])
    cluster_data = {}
    cluster_data['labels'] = kmeans.labels_
    cluster_data['cluster_centers'] = kmeans.cluster_centers_
    clusters = defaultdict(list)
    for i, label in enumerate(kmeans.labels_):
        bv = df.index[i]
        clusters[label].append(bv)
    cluster_data['clusters'] = clusters
    return cluster_data


