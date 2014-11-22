__author__ = 'telvis'

from nltk.metrics.distance import masi_distance, jaccard_distance
from cluster import HierarchicalClustering
import jsonlib2 as json

DISTANCE_THRESHOLD = 0.60
DISTANCE = jaccard_distance

def score(phrase1, phrase2):
    """
    using nltk distance metrics. For jaccard and masi, identical sets have a 0 distance.
    non-overlapping sets have a distance of 1.

    >>> jaccard_distance(set([1,2,3]),set([1,2,3]))
    0.0
    >>> jaccard_distance(set([1,2,3]),set([4]))
    1.0

    >>> masi_distance(set([1,2,3]),set([1,2,3]))
    0.0
    >>> masi_distance(set([1,2,3]),set([4]))
    1.0
    :param phrase1:
    :param phrase2:
    :return:
    """
    ret = DISTANCE(set(phrase1['es_phrase'].split()), set(phrase2['es_phrase'].split()))
    return ret


def hac(topic):
    """
    Use clusters.HierarchicalClustering
    https://pypi.python.org/pypi/cluster/1.1.0b1
    """
    phrases = [phrase for phrase in topic if phrase.get('es_phrase')]

    # Feed the class your data and the scoring function
    hc = HierarchicalClustering(phrases, score)

    # Cluster the data according to a distance threshold
    clusters = hc.getlevel(DISTANCE_THRESHOLD)
    # print "[hac]",len(clusters), json.dumps(clusters, indent=2)
    return clusters