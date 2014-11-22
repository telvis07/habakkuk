from pyes import ES
from pyes.query import MatchAllQuery, FilteredQuery, BoolQuery, MatchQuery, TextQuery
from pyes.filters import RangeFilter, TermFilter, QueryFilter
from pyes.utils import ESRange, ESRangeOp
import jsonlib2 as json
import logging
from django.conf import settings
from web.models import BibleText
logger = logging.getLogger(__name__)

def get_es_connection(host):
    ES_SETTINGS = settings.ES_SETTINGS
    logger.debug("Connecting to '%s'"%host )
    return ES(host, basic_auth=ES_SETTINGS.get('basic_auth'))

def bibleverse_facet(host,
                     index='habakkuk-*',
                     facet_terms=('bibleverse',),
                     doctype='habakkuk',
                     ts_field='created_at_date',
                     start=None,
                     end=None,
                     _date=None,
                     size=10,
                     search_text=None,
                     with_counts=False):
    """
    Perform faceted search query to find bibleverses in a date range.

    :param host: elasticsearch host
    :param index: elasticsearch index to search
    :param facet_terms: document field to facet on (usually 'bibleverse')
    :param doctype: elasticsearch document type to search for
    :param ts_field: field to search for time stamp
    :param start: starting timestamp value for range filter
    :param end: ending timestamp value for range filter
    :param _date: date to term filter for. assume start and end are not provided.
    :param size: number of facet results to return

    :return list of dicts: [{'bibleverse':'the-verse 1:1'}]
    """


    conn = get_es_connection(host)
    q = MatchAllQuery()

    # filter by date range
    if _date:
        # Filter for this 'date' timestamp
        q = FilteredQuery(q, TermFilter(field=ts_field,value=_date))
    elif start and end:
        # Filter for docs with timestamp in range [start, end]
        q = FilteredQuery(q, RangeFilter(qrange=ESRange(field=ts_field,
                                                        from_value=start,
                                                        to_value=end,
                                                        include_upper=False)))
    elif start:
        # Filter for docs with timestamp greater than 'start'
        q = FilteredQuery(q, RangeFilter(qrange=ESRangeOp(field=ts_field,
                                                          op1='gte',
                                                          value1=start)))
    elif end:
        # Filter for docs with timestamp less than 'end'
        q = FilteredQuery(q, RangeFilter(qrange=ESRangeOp(field=ts_field,
                                                          op1='lte',
                                                          value1=end)))

    q = q.search(size=0)

    # add the facet
    for term in facet_terms:
        if search_text:
            facet_filter = QueryFilter(BoolQuery(should=MatchQuery(field="text",
                                                                   text=search_text,
                                                                   operator='and')))
        else:
            facet_filter = None
        q.facet.add_term_facet(term,
                               order='count',
                               size=size,
                               facet_filter=facet_filter)

    logger.debug("[bibleverse_facet] query: '%s'"%json.dumps(q.serialize(), indent=2))
    resultset = conn.search(indices=index, doc_types=[doctype], query=q, search_type="count")

    ret = []
    debug_ret = []
    # get facet counts from the results
    for facet in resultset.facets:
        logger.debug("[bibleverse_facet] Total '%s:%s'"%(facet,resultset.facets[facet]['total']))
        for row in resultset.facets[facet]['terms']:
            ret.append({"bibleverse":row['term']})
            debug_ret.append({"bibleverse":row['term'], "count":row["count"]})

    logger.debug("[bibleverse_facet] Results: '%s'"%json.dumps(debug_ret))
    if with_counts:
        return debug_ret
    return ret

def bibleverse_text(bibleverses, translation="KJV"):
    """ Lookup the bibleverse text for the verses returned by bibleverse_facet

    :param bibleverses: list of dicts [{'bibleverse':'the-verse 1:1'}]
    :returns list of dicts: [{'bibleverse':'the-verse 1:1', 'text':'God says...'}]
    """
    for bv in bibleverses:
        try:
            bv['translation'] = translation
            bt = BibleText.objects.get(bibleverse=bv['bibleverse'], translation=bv['translation'])
            bv['text'] = bt.text
            bv['bibleverse_human'] = bt.bibleverse_human
        except BibleText.DoesNotExist:
            # This verse doesn't exist. probably a matching error.
            # set the text to 'None' so it get filtered before returning
            logger.error("The bibleverse '%(bibleverse)s' '%(translation)s' is not valid"%bv)
            bv['text'] = None

    # remove entries where text == None
    return filter(lambda x: x['text'], bibleverses)

def bibleverse_recommendations(bibleverses):
    return bibleverses

def get_scriptures_by_date(_date=None, st=None, et=None, size=10, search_text=None):
    ret = []
    ES_SETTINGS = settings.ES_SETTINGS
    hosts = ES_SETTINGS['hosts']
    search_index = ES_SETTINGS['search_index']
    ret = bibleverse_facet(host=hosts,
                           index=search_index,
                           start=st,
                           end=et,
                           _date=_date,
                           size=size,
                           search_text=search_text)
    ret = bibleverse_text(ret)
    ret = bibleverse_recommendations(ret)

    logger.debug("[get_scriptures_by_date] returns '%s",json.dumps(ret))
    return ret


def get_topics():
    """
    Fetch topics
    :return:
    """
    ret = []
    ES_SETTINGS = settings.ES_SETTINGS
    hosts = ES_SETTINGS['hosts']
    index =ES_SETTINGS['clusters_index']
    doctype = ES_SETTINGS["topics_es_type"]

    show_top_n = 3

    conn = get_es_connection(hosts)
    q = MatchAllQuery()
    q.search(size=1)
    resultset = conn.search(indices=index,
                            doc_types=[doctype],
                            query=q,
                            sort={ "date": { "order": "desc" }})
    ret = []
    for r in resultset:
        for clusters in r['cluster_topics']:
            for topics in clusters.get('topics', []):
                for topic in topics[:show_top_n]:
                    if not topic.get('es_phrase'):
                        continue
                    ret.append({
                      'es_phrase' : topic['es_phrase'],
                      'bibleverse' : 'test 1:1',
                      "search_url" : "http://localhost:8000/biblestudy/?search=enemies+good"
                    })

    return {
        'count' : len(ret),
        'topics' : ret
    }