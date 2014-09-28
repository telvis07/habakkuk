__author__ = 'telvis'
from topic_analysis import topic_extraction
from topic_analysis import clustering
import jsonlib2 as json
from datetime import datetime, timedelta
# from topic_analysis.topics import *

BIBLEVERSE_LIST = '/Users/telvis/work/habakkuk/analysis/join_data/bibleverses.txt'


def main(et, top_n=3, n_clusters=6, num_days=15):

    st = et - timedelta(days=num_days)


    valid_bv_set = set([line.strip() for line in open(BIBLEVERSE_LIST)])
    # create a dictionary[date] = counter
    data = []
    for created_at_date, _counter in clustering.get_data_from_store(st=st, et=et, valid_bv_set=valid_bv_set):
        data.append((created_at_date, _counter))
    data = dict(data)

    # filter for most common bibleverses, returns a DataFrame
    df = clustering.get_most_common_df(data, num=top_n)

    # get bv counts and max counts
    top_df = clustering.get_count_features_df(df)
    #print top_df

    # perform clustering
    cluster_data = clustering.build_clusters(top_df, n_clusters=n_clusters)
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
        'start_date' : st.strftime("%Y-%m-%d"),
        'end_date' : et.strftime("%Y-%m-%d"),
        'num_days' : num_days,
        'n_clusters' : n_clusters,
        'top_n' : top_n,
        'cluster_topics' : saved_cluster_data
    }
    topic_extraction.save_topic_clusters(doc)
    print json.dumps(doc, indent=2)
    return doc
