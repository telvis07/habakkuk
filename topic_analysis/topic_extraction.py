__author__ = 'telvis'


from pyes.query import MatchAllQuery, FilteredQuery, MatchQuery, TermQuery
from pyes.filters import RangeFilter, TermFilter, TermsFilter, ANDFilter
from pyes.utils import ESRange
from pyes import ES

import re
import logging
logger = logging.getLogger(__name__)

from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer, TfidfTransformer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from topic_analysis.phrase_clustering import hac

from django.conf import settings
import copy
import jsonlib2 as json



class ESSettings:
    """
    Class to store Elasticsearch settings from django
    """
    def __init__(self):
        ES_SETTINGS = settings.ES_SETTINGS

        self.hosts = ES_SETTINGS['hosts']
        self.search_index = ES_SETTINGS['search_index']
        self.topics_index = ES_SETTINGS['topics_index']
        self.search_es_type = ES_SETTINGS['search_es_type']
        self.clusters_es_type = ES_SETTINGS['clusters_es_type']
        self.phrases_es_type = ES_SETTINGS['phrases_es_type']
        self.basic_auth = ES_SETTINGS.get('basic_auth')


def get_es_connection(host=None):
    es_settings = ESSettings()
    if not host:
        host = es_settings.hosts

    logger.debug("Connecting to '%s'"%host )
    return ES(host, basic_auth=es_settings.basic_auth)


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
    conn = get_es_connection()
    es_settings = ESSettings()
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
    resultset = conn.search(indices=es_settings.search_index,
                            doc_types=[es_settings.search_es_type],
                            query=q,
                            size=200)
    res = list()
    for r in resultset:
        t = re.sub("[@#]\w+(?:$|\W)","", r['text'])
        res.append(t)
    return res


def phrase_search(topics, bibleverses, start, end, ts_field='created_at_date'):
    conn = get_es_connection()
    es_settings = ESSettings()
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
            resultset = conn.search(indices=es_settings.search_index,
                                    doc_types=[es_settings.search_es_type],
                                    query=q,
                                    size=1)

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
                topic_term['bibleverse'] = r['bibleverse']

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
    conn = get_es_connection()
    es_settings = ESSettings()
    for cluster in doc["cluster_topics"]:
        if not cluster.get('num_topics',0):
            continue

    ret = conn.index(doc=doc, index=es_settings.topics_index, doc_type=es_settings.clusters_es_type)
    logger.debug(ret)


def rank_phrases_and_store(doc):
    """
    rank phrases by cluster size, score and es_score, etc
    :param doc:
    :return:
    """
    ret = []
    rank = 1
    # save the 'date'
    _date = doc['date']
    import sys

    # loop over clusters, ranked by the topic_sort_key
    for cluster in sorted(doc['cluster_topics'], key=topic_sort_key):
        for topic in cluster.get('topics', []):
            # now perform hierarchical clustering to group phrases
            # similar phrases together.
            phrase_clusters = hac(topic)
            for cluster in phrase_clusters:
                # now get the first entry from each phrase_cluster
                # assumes the other entries and similar enough to ignore
                phrase = sorted(cluster, key=phrase_sort_key, reverse=True)[0]

                # See phrase_search() for is_spam meaning
                if phrase.get('is_spam'):
                    continue

                # append to the list with its rank
                ret.append({
                   'phrase' : phrase['es_phrase'],
                   'bibleverse' : phrase['bibleverse'],
                   "search_text" : "+".join(phrase['text'].split()),
                   "rank" : rank,
                   "date" : _date
                })
                rank += 1

    # Now store the ranked results in ES
    conn = get_es_connection()
    es_settings = ESSettings()


    q = TermQuery(field='date', value=_date)
    result = conn.delete_by_query(es_settings.topics_index, [es_settings.phrases_es_type], q)
    logger.info("[rank_results] : delete complete. index=%s, type=%s, query='%s', failed=%s",
                es_settings.topics_index,
                es_settings.phrases_es_type,
                json.dumps(q.search().serialize()),
                result['_indices'][es_settings.topics_index]['_shards']['failed'])
    for phrase_doc in ret:
        conn.index(doc=phrase_doc, index=es_settings.topics_index, doc_type=es_settings.phrases_es_type)
    logger.info("Wrote %d docs to index=%s, type=%s, date=%s",
                len(ret),
                es_settings.topics_index,
                es_settings.phrases_es_type,
                _date)

def topic_sort_key(x):
    return x.get('num_topics',0)


def phrase_sort_key(x):
    x.get('weight', 0)


