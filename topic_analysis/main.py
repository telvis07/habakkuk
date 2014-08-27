__author__ = 'telvis'
from topic_analysis import topic_extraction
from topic_analysis import clustering
import jsonlib2 as json
from datetime import datetime, timedelta
# from topic_analysis.topics import *

BIBLEVERSE_LIST = '/home/telvis/habakkuk/analysis/join_data/bibleverses.txt'


def main():
    top_n=3
    n_clusters=6
    num_days=15

    # st = datetime.today() - timedelta(days=num_days)
    # et = datetime.today()
    st = datetime(2014, 05, 15)
    et = datetime(2014, 05, 30)

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
        topics = topic_extraction.topic_extraction(corpus, bv_tokens, data=data)
        if topics:
            data['topics'] = topics
            print "\n"
        saved_cluster_data.append(data)

    #print_clusters(df, cluster_data['clusters'])
    print json.dumps(saved_cluster_data, indent=2)
    # return df, cluster_data
