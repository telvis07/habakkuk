__author__ = 'telvis'


from pyes.query import MatchAllQuery, FilteredQuery, MatchQuery
from pyes.filters import RangeFilter, TermFilter, TermsFilter, ANDFilter
from pyes.utils import ESRange
import re
import sys

from sklearn import decomposition
from sklearn.feature_extraction.text import TfidfVectorizer, TfidfTransformer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from django.conf import settings
from web.search import get_es_connection
import jsonlib2 as json
import copy

ES_SETTINGS = settings.ES_SETTINGS
hosts = ES_SETTINGS['hosts']
SEARCH_INDEX = ES_SETTINGS['search_index']
CLUSTERS_INDEX ='clusters-all'
TOPICS_DOC_TYPE="topics"

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
                'nlt', 'kjv']

    # print bv_tokens
    vectorizer.set_params(stop_words=set(list(ENGLISH_STOP_WORDS)+stoplist+bv_stop_tokens))
    counts = vectorizer.fit_transform(corpus)

    tfidf = TfidfTransformer().fit_transform(counts)
    feature_names = vectorizer.get_feature_names()
    data['num_topic_features'] = len(feature_names)
    data['num_topic_samples'] = n_samples
    data['num_topics'] = n_topics


    try:
        nmf = decomposition.NMF(n_components=n_topics, random_state=42).fit(tfidf)
    except Exception, ex:
        print "decomposition.NMF failed", ex, bv_stop_tokens, data, "n_topics", n_topics
        return []

    cluster_topics = []
    for topic_idx, topic in enumerate(nmf.components_):
        sorted_topics = topic.argsort()[:-n_top_words - 1:-1]
        cluster_topics.append([{'text': feature_names[i], 'weight':topic[i]} for i in sorted_topics])

    return cluster_topics


def get_text_from_es(conn, bibleverse, start, end, ts_field='created_at_date'):
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
            # print json.dumps(q.serialize(), indent=2)
            resultset = conn.search(indices=["habakkuk-all"], doc_types=["habakkuk"], query=q, size=1)
            # print json.dumps(resultset[0], indent=2)

            for r in resultset:
                terms = topic_term['text'].split()
                regex = "(?P<phrase>{}.*{}[\w\s]*)".format(*terms)
                # print "regex",regex
                ma = re.search(regex, r.text.lower())
                if not ma:
                    print "ERROR. Query={}, text={}".format(regex.encode('ascii', 'ignore'), r.text.encode('ascii', 'ignore'))
                    continue
                # print "topic_term '{}', phrase_match '{}', score: {}".format(topic_term['text'],
                #                                                              ma.group('phrase'),
                #                                                              r._meta.score)
                topic_term['es_phrase'] = ma.group('phrase')
                topic_term['es_score'] = r._meta.score
                topic_term['final_score'] = topic_term['weight'] * topic_term['es_score']
                topic_term['tweet_text'] = r.text.encode('ascii', 'ignore')

                if not is_spam and has_spam_text(topic_term['es_phrase']):
                    is_spam = True


                #
                # res.append({'topic_term': topic_term['text'],
                #             'phrase_match':ma.group,
                #             'es_score' : r._meta.score})
        # print json.dumps(topic, indent=2)

        sorted_topic = sorted(topic,
                              key=lambda x: x.get('final_score', 0.0),
                              reverse=True)
        if is_spam:
            for topic_term in topic:
                topic_term['is_spam'] = True
        sorted_topics.append(copy.deepcopy(sorted_topic))
        # print json.dumps(sorted_topic, indent=2)
    return sorted_topics

def has_spam_text(text):
    return text.find('http') != -1

def build_corpus(st, et, bibleverses):
    bv_tokens = []
    [bv_tokens.extend(bv.replace(":"," ").split()) for bv in bibleverses]

    conn = get_es_connection(hosts)
    corpus = []
    for bv in bibleverses:
        ret = get_text_from_es(conn, bv, st, et)
        corpus.append(" ".join(ret))
        # print len(" ".join(ret))
    return (bv_tokens, corpus)


def save_topic_clusters(doc):
    # get es conn
    conn = get_es_connection(hosts)
    for cluster in doc["cluster_topics"]:
        if not cluster['num_topics']:
            continue

    ret = conn.index(doc=doc, index=CLUSTERS_INDEX, doc_type=TOPICS_DOC_TYPE)
    print ret