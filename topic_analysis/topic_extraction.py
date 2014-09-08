__author__ = 'telvis'


from pyes.query import MatchAllQuery, FilteredQuery
from pyes.filters import RangeFilter, TermFilter, ANDFilter
from pyes.utils import ESRange
import re

from sklearn import decomposition
from sklearn.feature_extraction.text import TfidfVectorizer, TfidfTransformer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

def nmf_topic_extraction(corpus, bv_stop_tokens, n_features = 5000, n_top_words = 5, n_topics = 3, data={}):
    n_samples = len(corpus)

    # ensure we don't ask for more topics than we have samples
    # this happens when we there are only a few bibleverses in a cluster
    n_topics = min(n_samples, n_topics)


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
    #q = MatchAllQuery()
    filters = []
    # filters.append(RangeFilter(qrange=ESRangeOp(field=ts_field, op1='gte',value1=start)))
    filters.append(
        RangeFilter(qrange=ESRange(field=ts_field,
                                   from_value=start,
                                   to_value=end,
                                   include_upper=False))
    )
    filters.append(TermFilter(field="bibleverse",value=bibleverse))
    q = FilteredQuery(MatchAllQuery(), ANDFilter(filters))


    q = q.search(size=200)
    resultset = conn.search(indices=["habakkuk-all"], doc_types=["habakkuk"], query=q, size=200)
    # print "Total results %s %s docs"%(bibleverse, resultset.total)
    res = list()
    for r in resultset:
        t = re.sub("[@#]\w+(?:$|\W)","", r['text'])
        res.append(t)
    return res

def build_corpus(st, et, bibleverses):
    bv_tokens = []
    [bv_tokens.extend(bv.replace(":"," ").split()) for bv in bibleverses]
    from pyes import ES


    # get es conn
    conn = ES('192.168.117.4:9201')
    corpus = []
    for bv in bibleverses:
        ret = get_text_from_es(conn, bv, st, et)
        corpus.append(" ".join(ret))
        # print len(" ".join(ret))
    return (bv_tokens, corpus)