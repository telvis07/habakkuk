from pyes import ES
from pyes.query import MatchAllQuery, FilteredQuery, BoolQuery, MatchQuery
from pyes.filters import RangeFilter, TermFilter, QueryFilter, TermsFilter
from pyes.utils import ESRange, ESRangeOp
import jsonlib2 as json
import logging
from django.conf import settings
from web.models import BibleText
logger = logging.getLogger(__name__)


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
    es_settings = ESSettings()
    ret = bibleverse_facet(host=es_settings.hosts,
                           index=es_settings.search_index,
                           start=st,
                           end=et,
                           _date=_date,
                           size=size,
                           search_text=search_text)
    ret = bibleverse_text(ret)
    ret = bibleverse_recommendations(ret)

    logger.debug("[get_scriptures_by_date] returns '%s",json.dumps(ret))
    return ret


def get_topics(size=10, offset=0, topic_name=None):
    """
    rank results by cluster size, score and es_score, etc
    :param doc:
    :return:
    """
    logger.debug("[get_topics] size={}, offset={}".format(size, offset))

    ret = []

    conn = get_es_connection()
    es_settings = ESSettings()
    q = build_topic_query(topic_name)
    q = q.search(sort={ "date": { "order": "desc" }, "rank" : {"order" : "asc"}})
    resultset = conn.search(indices=es_settings.topics_index,
                            doc_types=[es_settings.phrases_es_type],
                            query=q,
                            size=size, start=offset)
    resultset = [r for r in resultset]

    num_phrases = 0
    for phrase in resultset:
        if num_phrases == 0:
            ret.append({
                'bibleverse' : phrase['bibleverse'],
                'phrases' : []
            })

        num_phrases += 1
        if phrase['bibleverse'] == ret[-1]['bibleverse']:
            ret[-1]['phrases'].append({
               'phrase' : phrase['phrase'],
               'bibleverse' : phrase['bibleverse'],
               "search_url" : settings.BIBLESTUDY_SEARCH_URL+phrase['search_text']
            })
        else:
            ret.append({
                'bibleverse' : phrase['bibleverse'],
                'phrases' : [{
                                 'phrase' : phrase['phrase'],
                                 'bibleverse' : phrase['bibleverse'],
                                 "search_url" : settings.BIBLESTUDY_SEARCH_URL+phrase['search_text']
                             }]
            })

    return {
        'count' : num_phrases,
        'topics' : ret,
        'topic_name' : topic_name,
        'more_results' : True if len(resultset) else False
    }

def build_topic_query(topic_name):
    if not topic_name:
        q = MatchAllQuery()
    elif topic_name.lower() == 'newyears':
        q = FilteredQuery(MatchAllQuery(), TermsFilter(field='date',
                                                       values=['2015-01-01']))
    elif topic_name.lower() == 'memorialday':
        q = FilteredQuery(MatchAllQuery(), TermsFilter(field='date',
                                                       values=['2014-05-26']))
    elif topic_name.lower() == 'independence':
        q = FilteredQuery(MatchAllQuery(), TermsFilter(field='date',
                                                       values=['2014-07-04']))
    elif topic_name.lower() == 'valentines':
        q = FilteredQuery(MatchAllQuery(), TermsFilter(field='date',
                                                       values=['2014-02-14']))
    elif topic_name.lower() == 'thanksgiving':
        q = FilteredQuery(MatchAllQuery(), TermsFilter(field='date',
                                                       values=['2014-11-27']))
    elif topic_name.lower() == 'christmas':
        q = FilteredQuery(MatchAllQuery(), TermsFilter(field='date',
                                                       values=['2014-12-25']))
    else:
        logger.warning("[build_topic_query] Did not find a topic for {}".format(topic_name))
        q = MatchAllQuery()

    return q