__author__ = 'telvis'
from topic_analysis import topic_extraction
from topic_analysis import topic_clustering
from topic_analysis.bibleverse_list import BIBLEVERSE_LIST
import jsonlib2 as json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def main(_dt, top_n=3, n_clusters=6, num_days=15):

    # TODO: For some reason I need to increment the date by 1 day
    # to get all the tweets and bv counts. Probably due to UTC/GMT
    # shenanigans.
    et = _dt + timedelta(days=1)
    st = et - timedelta(days=num_days)

    valid_bv_set = set(BIBLEVERSE_LIST)

    # create a dictionary[date] = counter
    data = []
    for created_at_date, _counter in topic_clustering.get_data_from_store(st=st, et=et, valid_bv_set=valid_bv_set):
        data.append((created_at_date, _counter))
    data = dict(data)

    # filter for most common bibleverses, returns a DataFrame
    df = topic_clustering.get_most_common_df(data, num=top_n)

    # get bv counts and max counts
    top_df = topic_clustering.get_count_features_df(df)
    #print top_df

    # perform clustering
    cluster_data = topic_clustering.build_clusters(top_df, n_clusters=n_clusters)
    cluster_data['dates'] = data.keys()

    saved_cluster_data = []

    for label in cluster_data['clusters']:
        # print df.ix[clusters[label]][["count_entries", "max"]]
        data = {}
        data['label'] = int(label)
        data['points'] =  []
        data['bibleverses'] = []
        data['cluster_size'] = len(cluster_data['clusters'][label])

        for bibleverse in cluster_data['clusters'][label]:
            data['points'].append((df["count_entries"][bibleverse], df["max"][bibleverse]))
            data['bibleverses'].append(bibleverse)

        # topic analysis
        bv_tokens, corpus = topic_extraction.build_corpus(st, et, cluster_data['clusters'][label])
        topics = topic_extraction.nmf_topic_extraction(corpus, bv_tokens, data=data)
        if topics:
            data['topics'] = topics
            data['topics'] = topic_extraction.phrase_search(data['topics'],
                                           data['bibleverses'],
                                           st,
                                           et)
        saved_cluster_data.append(data)

    #print_clusters(df, cluster_data['clusters'])
    doc = {
        'date' : _dt.strftime("%Y-%m-%d"),
        'start_date' : st.strftime("%Y-%m-%d"),
        'end_date' : et.strftime("%Y-%m-%d"),
        'num_days' : num_days,
        'n_clusters' : n_clusters,
        'top_n' : top_n,
        'cluster_topics' : saved_cluster_data
    }
    topic_extraction.save_topic_clusters(doc)
    topic_extraction.rank_phrases_and_store(doc)
    logger.debug("{}".format(json.dumps(doc, indent=2)))
    return doc
