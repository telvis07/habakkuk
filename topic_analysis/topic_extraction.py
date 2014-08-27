__author__ = 'telvis'


from pyes.query import MatchAllQuery, FilteredQuery
from pyes.filters import RangeFilter, TermFilter, ANDFilter
from pyes.utils import ESRange
import re

from sklearn import decomposition
from sklearn.feature_extraction.text import TfidfVectorizer, TfidfTransformer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

def topic_extraction(corpus, bv_tokens, n_features = 5000, n_top_words = 10, n_topics = 3, data={}):
    n_samples = len(corpus)

    # vectorize the tweet text using the most common word
    # frequency with TF-IDF weighting (without the top 5% stop words)
    vectorizer = TfidfVectorizer(max_features=n_features,
                                 ngram_range=(2,2)
                                 )
    stoplist = ['retweet', 'rt', 'http', 'things', 'christ', 'lord', 'god', 'shall', 'jesus',
                'nlt', 'kjv']

    # print bv_tokens
    vectorizer.set_params(stop_words=set(list(ENGLISH_STOP_WORDS)+stoplist+bv_tokens))
    counts = vectorizer.fit_transform(corpus)

    tfidf = TfidfTransformer().fit_transform(counts)
    feature_names = vectorizer.get_feature_names()
    data['num_topic_features'] = len(feature_names)
    data['num_topic_samples'] = n_samples


    try:
        nmf = decomposition.NMF(n_components=n_topics, random_state=42).fit(tfidf)
    except:
        print "decomposition.NMF failed"
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


    q = q.search(size=100)
    resultset = conn.search(indices=["habakkuk-all"], doc_types=["habakkuk"], query=q, size=100)
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