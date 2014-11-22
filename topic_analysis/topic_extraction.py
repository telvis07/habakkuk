__author__ = 'telvis'


from pyes.query import MatchAllQuery, FilteredQuery, MatchQuery
from pyes.filters import RangeFilter, TermFilter, TermsFilter, ANDFilter
from pyes.utils import ESRange

import re, sys
import logging
logger = logging.getLogger(__name__)

from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer, TfidfTransformer, CountVectorizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from sklearn.cluster import Ward
import numpy as np
from sklearn.metrics import jaccard_similarity_score
from sklearn.metrics.pairwise import pairwise_distances
from topic_analysis.phrase_clustering import hac

from django.conf import settings
from web.search import get_es_connection
import copy
import jsonlib2 as json

ES_SETTINGS = settings.ES_SETTINGS
hosts = ES_SETTINGS['hosts']
SEARCH_INDEX = ES_SETTINGS['search_index']
CLUSTERS_INDEX =ES_SETTINGS['clusters_index']
TOPICS_DOC_TYPE= ES_SETTINGS["topics_es_type"]

def nmf_topic_extraction(corpus, bv_stop_tokens, n_features = 5000, n_top_words = 5, n_topics = 3, data={}):
    n_samples = len(corpus)

    # ensure we don't ask for more topics than we have samples
    # this happens when we there are only a few bibleverses in a cluster
    n_topics = min(n_samples, n_topics)
    if n_topics==2:
        n_topics = 1


    # vectorize the tweet text using the most common word
    # frequency with TF-IDF weighting (without the top 5% stop words)
    vectorizer = TfidfVectorizer(max_features=n_features,
                                 ngram_range=(2,2)
                                 )
    stoplist = ['retweet', 'rt', 'http', 'things', 'christ', 'lord', 'god', 'shall', 'jesus',
                'nlt', 'kjv', 'prov']

    try:
        vectorizer.set_params(stop_words=set(list(ENGLISH_STOP_WORDS)+stoplist+bv_stop_tokens))
        counts = vectorizer.fit_transform(corpus)

        tfidf = TfidfTransformer().fit_transform(counts)
        feature_names = vectorizer.get_feature_names()
    except Exception, ex:
        logger.exception("Tfidf analysis failed ex={}, bv={}, data={}, n_topics={}".format(ex, bv_stop_tokens, data, n_topics))
        return []

    data['num_topic_features'] = len(feature_names)
    data['num_topic_samples'] = n_samples
    data['num_topics'] = n_topics


    try:
        nmf = NMF(n_components=n_topics, random_state=42).fit(tfidf)
    except Exception, ex:
        logger.exception("decomposition.NMF failed {} {} {} {} {}".format(ex, bv_stop_tokens, data, "n_topics", n_topics))
        return []

    cluster_topics = []
    for topic_idx, topic in enumerate(nmf.components_):
        sorted_topics = topic.argsort()[:-n_top_words - 1:-1]
        cluster_topics.append([{'text': feature_names[i], 'weight':topic[i]} for i in sorted_topics])

    return cluster_topics


def get_text_from_es(bibleverse, start, end, ts_field='created_at_date'):
    conn = get_es_connection(hosts)
    filters = []
    filters.append(
        RangeFilter(qrange=ESRange(field=ts_field,
                                   from_value=start.strftime("%Y-%m-%d"),
                                   to_value=end.strftime("%Y-%m-%d"),
                                   include_upper=False))
    )
    filters.append(TermFilter(field="bibleverse",value=bibleverse))
    q = FilteredQuery(MatchAllQuery(), ANDFilter(filters))


    q = q.search(size=100)
    resultset = conn.search(indices=["habakkuk-all"], doc_types=["habakkuk"], query=q, size=200)
    res = list()
    for r in resultset:
        t = re.sub("[@#]\w+(?:$|\W)","", r['text'])
        res.append(t)
    return res

def phrase_search(topics, bibleverses, start, end, ts_field='created_at_date'):
    conn = get_es_connection(hosts)
    sorted_topics = []

    for topic in topics:
        is_spam = False
        for topic_term in topic:
            filters = []
            filters.append(
                RangeFilter(qrange=ESRange(field=ts_field,
                                           from_value=start.strftime("%Y-%m-%d"),
                                           to_value=end.strftime("%Y-%m-%d"),
                                           include_upper=False))
            )
            filters.append(TermsFilter(field="bibleverse", values=bibleverses))
            q = MatchQuery('text', topic_term['text'], type='phrase', slop=50)
            q = FilteredQuery(q, ANDFilter(filters))
            q = q.search(size=1)
            resultset = conn.search(indices=SEARCH_INDEX, doc_types=["habakkuk"], query=q, size=1)

            for r in resultset:
                terms = topic_term['text'].split()
                regex = u"(?P<phrase>[a-z\s'\u2019]*{}.*{}[a-z\s']*)".format(*terms)
                # print "regex",regex
                ma = re.search(regex, r.text.lower())
                if not ma:
                    continue
                topic_term['es_phrase'] = ma.group('phrase').strip()
                topic_term['es_score'] = r._meta.score
                topic_term['final_score'] = topic_term['weight'] * topic_term['es_score']
                topic_term['tweet_text'] = r.text.encode('ascii', 'ignore')

                if not is_spam and has_spam_text(topic_term['es_phrase']):
                    is_spam = True

        sorted_topic = sorted(topic,
                              key=lambda x: x.get('final_score', 0.0),
                              reverse=True)
        if is_spam:
            for topic_term in topic:
                topic_term['is_spam'] = True
        sorted_topics.append(copy.deepcopy(sorted_topic))
    return sorted_topics

def has_spam_text(text):
    return text.find('http') != -1

def build_corpus(st, et, bibleverses):
    bv_tokens = []
    [bv_tokens.extend(bv.replace(":"," ").split()) for bv in bibleverses]
    for bv in bibleverses:
        ma = re.match("i{1,3}_(?P<book>\w+)", bv)
        if ma:
            bv_tokens.append(ma.group('book'))

    corpus = []
    for bv in bibleverses:
        ret = get_text_from_es(bv, st, et)
        corpus.append(" ".join(ret))
    return (bv_tokens, corpus)


def save_topic_clusters(doc):
    # get es conn
    conn = get_es_connection(hosts)
    for cluster in doc["cluster_topics"]:
        if not cluster.get('num_topics',0):
            continue

    ret = conn.index(doc=doc, index=CLUSTERS_INDEX, doc_type=TOPICS_DOC_TYPE)
    logger.debug(ret)


# TODO: store the ranked results as another type in clusters-all
def rank_results(doc):
    """
    rank results by cluster size, score and es_score, etc
    :param doc:
    :param show_top_n:
    :return:
    """
    ret = []

    for cluster in sorted(doc['cluster_topics'], key=topic_sort_key):
        for topic in cluster.get('topics', []):
            phrase_clusters = hac(topic)
            for cluster in phrase_clusters:
                phrase = sorted(cluster, key=phrase_sort_key)[0]
                ret.append({
                   'es_phrase' : phrase['es_phrase'],
                   'bibleverse' : 'test 1:1',
                   "search_url" : "http://localhost:8000/biblestudy/?search=enemies+good"
                })

    # print json.dumps(ret, indent=2)
    # TODO: store the sorted topics in ES. include the date in each record
    print "To save", json.dumps(ret, indent=2)


def topic_sort_key(x):
    return x['num_topics']

def phrase_sort_key(x):
    x.get('weight', 0)

def calc_similarity(topic):
    """
    compute the similarity of the list of phrases in this topic
    :param topic:
    :return:
    """
    # http://scikit-learn.org/stable/modules/generated/sklearn.metrics.jaccard_similarity_score.html
    # TODO: Find the max score per topic
    scores = np.zeros((len(topic), len(topic)))
    for i in xrange(len(topic)):

        for j in xrange(i+1, len(topic)):
            if i==j:
                continue
            if not topic[i].get('es_phrase') or not topic[j].get('es_phrase'):
                scores[i][j] = -1
                continue

            print "'{} {}' '{} {}'".format(i,
                                           topic[i]['es_phrase'],
                                            j,
                                            topic[j]['es_phrase'])
            vectorizer = CountVectorizer()
            counts = vectorizer.fit_transform([
                topic[i]['es_phrase'],
                topic[j]['es_phrase']
            ])
            counts = counts.toarray()
            print counts[0]
            print counts[1]
            score = pairwise_distances(counts[0], counts[1], metric="euclidean")
            print score
            scores[i][j] = score

    print scores


def calc_similarity_ward(topic):
    """
    compute the similarity of the list of phrases in this topic using heirarchical clustering
    not used but just keeping around as a working example.
    :param topic:
    :return:
    """
    # http://scikit-learn.org/stable/modules/generated/sklearn.metrics.jaccard_similarity_score.html
    # TODO: Find the max score per topic

    phrases = [phrase.get('es_phrase') for phrase in topic if phrase.get('es_phrase')]
    print json.dumps(phrases, indent=2)

    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(phrases)
    X = X.toarray()
    print X
    ward = Ward(n_clusters=2).fit(X)
    print ward.labels_
    #sys.exit(0)


