from pyes import ES
from pyes.query import MatchAllQuery, FilteredQuery
from pyes.filters import RangeFilter
from pyes.utils import ESRange
import jsonlib2 as json
import logging
logger = logging.getLogger('search')

def bibleverse_facet(host='localhost:9200',
                           terms=['bibleverse'],
                           _type='habakkuk',
                           start=None,
                           end=None,
                           size=10):
    ret = []
    conn = ES(host)
    q = MatchAllQuery()
    if start and end:
        q = FilteredQuery(q, RangeFilter(qrange=ESRange('created_at_date',start,end,include_upper=False)))
    elif start:
        pass # todo
    elif end:
        pass # todo
    q = q.search(size=0)

    for term in terms:
        q.facet.add_term_facet(term,order='count',size=size)

    logger.info("Query: '%s'"%json.dumps(q.serialize(),indent=2))
    resultset = conn.search(query=q, indices=_type+'-*', doc_types=[_type])

    for facet in resultset.facets:
        print "Total",facet,resultset.facets[facet]['total']
        for row in resultset.facets[facet]['terms']:
            ret.append((row['term']), row['count'])

    logger.info("Results: '%s'"%json.dumps(ret,indent=2))
    # TODO lookup bibleverse text
    return ret

def get_scriptures_by_date(st=None, et=None):
    ret = []

    # todo
    # ret = bibleverse_facet(st, et)
    # ret = bibleverse_text(ret)
    # ret = bibleverse_recommendations(ret)

    # TODO: call ES. sort by the date and get the 'latest'
    ret = [{"bibleverse":"John 3:16",
      "text":"For God so loved the world that he gave his one and only Son,"
      "that whoever believes in him shall not perish but have eternal life.",
      "recommendations":["Book 1:1", "Book 1:2", "Book 1:3"]},
      {"bibleverse":"1 John 4:19",
      "text":"We love because he first loved us.",
      "recommendations":["Book 2:1", "Book 2:2", "Book 2:3"]},
      {"bibleverse":"1 Corinthians 13:4",
      "text":"Love is patient, love is kind. It does not envy, it does not boast, it is not proud.",
      "recommendations":["Book 2:1", "Book 2:2", "Book 2:3"]},
      {"bibleverse":"1 Corinthians 13:13",
      "text":"And now these three remain: faith, hope and love. But the greatest of these is love.",
      "recommendations":["Book 2:1", "Book 2:2", "Book 2:3"]},
      {"bibleverse":"Psalm 37:23",
      "text":"The steps of a good man are ordered by the Lord: and he delighteth in his way.",
      "recommendations":["Book 2:1", "Book 2:2", "Book 2:3"]},
    ]

    return ret