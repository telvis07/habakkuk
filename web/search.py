from pyes import ES
from pyes.query import MatchAllQuery, FilteredQuery
from pyes.filters import RangeFilter, TermFilter
from pyes.utils import ESRange, ESRangeOp
import jsonlib2 as json
import logging
from django.conf import settings
logger = logging.getLogger('search')

def get_es_connection(host):
    return ES(host)

def bibleverse_facet(host='localhost:9200',
                     index='habakkuk-*',
                     facet_terms=('bibleverse',),
                     doctype='habakkuk',
                     ts_field='created_at_date',
                     start=None,
                     end=None,
                     _date=None,
                     size=10):
    ret = []
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
                                                          op='gte',
                                                          value=start)))
    elif end:
        # Filter for docs with timestamp less than 'end'
        q = FilteredQuery(q, RangeFilter(qrange=ESRangeOp(field=ts_field,
                                                          op='lte',
                                                          value=end)))

    q = q.search(size=0)

    # add the facet
    for term in facet_terms:
        q.facet.add_term_facet(term, order='count', size=size)

    logger.info("Query: '%s'"%json.dumps(q.serialize(),indent=2))
    resultset = conn.search(indices=index+'-*', doc_types=[doctype], query=q, search_type="count")

    # get facet counts from the results
    for facet in resultset.facets:
        logger.debug("Total '%s'"%facet,resultset.facets[facet]['total'])
        for row in resultset.facets[facet]['terms']:
            ret.append((row['term'], row['count']))

    logger.info("Results: '%s'"%json.dumps(ret,indent=2))
    return ret

def bibleverse_text(bibleverses):
    return bibleverses

def bibleverse_recommendations(bibleverses):
    return bibleverses

def get_scriptures_by_date(_date=None, st=None, et=None, size=10):
    ret = []
    ES_SETTINGS = settings.ES_SETTINGS
    hosts = ES_SETTINGS['hosts']
    search_index = ES_SETTINGS['search_index']
    ret = bibleverse_facet(host=hosts, index=search_index, start=st, end=et, _date=_date, size=size)
    ret = bibleverse_text(ret)
    ret = bibleverse_recommendations(ret)

    logger.info("get_scriptures_by_date: returns '%s",json.dumps(ret))
    return ret