__author__ = 'telvis'

from django.core.management.base import BaseCommand
# from optparse import make_option

from topic_analysis.clustering import *

BIBLEVERSE_LIST = '/home/telvis/habakkuk/analysis/join_data/bibleverses.txt'

class Command(BaseCommand):
    option_list = BaseCommand.option_list + ()

    def handle(self, *args, **options):
        top_n=3
        n_clusters=6
        num_days=15

        valid_bv_set = set([line.strip() for line in open(BIBLEVERSE_LIST)])
        # create a dictionary[date] = counter
        data = []
        for created_at_date, _counter in get_data_from_store(num_days=num_days, valid_bv_set=valid_bv_set):
            data.append((created_at_date, _counter))
        data = dict(data)

        # filter for most common bibleverses, returns a DataFrame
        df = get_most_common_df(data, num=top_n)

        # get bv counts and max counts
        top_df = get_count_features_df(df)
        #print top_df

        # perform clustering
        cluster_data = build_clusters(top_df, n_clusters=n_clusters)
        cluster_data['dates'] = data.keys()

        clusters = []

        for label in cluster_data['clusters']:
            # print df.ix[clusters[label]][["count_entries", "max"]]
            data = {}
            data['label'] = int(label)
            data['points'] =  []
            data['bibleverses'] = []
            data['cluster_center']= 0.00

            for bibleverse in cluster_data['clusters'][label]:
                data['points'].append((df["count_entries"][bibleverse], df["max"][bibleverse]))
                data['bibleverses'].append(bibleverse)
            clusters.append(data)
            print data

        #print_clusters(df, cluster_data['clusters'])
        print json.dumps(clusters, indent=2)
        # return df, cluster_data

