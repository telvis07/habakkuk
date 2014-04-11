#!/usr/bin/env python
"""
Simple faceting on the habakkuk index for a date range
"""
from pyes import ES
from pyes.query import MatchAllQuery, StringQuery, TermQuery, FilteredQuery
from pyes.filters import RangeFilter
from pyes.utils import ESRange
from pyes.facets import DateHistogramFacet, HistogramFacet
from optparse import OptionParser
import sys
from datetime import datetime
import jsonlib2 as json

def term_facet(host='localhost:9200',
               terms=['bibleverse'],
               _type='habakkuk',
               date_filter=[],
               size=10):
    ret = []
    conn = ES(host)
    q = MatchAllQuery()
    if date_filter:
        start,end = date_filter
        q = FilteredQuery(q, RangeFilter(qrange=ESRange('created_at_date',start,end,include_upper=False)))

    q = q.search(size=0)
    for term in terms:
        q.facet.add_term_facet(term,order='count',size=size)
        
    print json.dumps(json.loads(q.to_search_json()),indent=2)

    resultset = conn.search(query=q, indices=_type+'-*', doc_types=[_type])
    for facet in resultset.facets:
        print "Total",facet,resultset.facets[facet]['total']
        for row in resultset.facets[facet]['terms']:
            print "\t",row['term'],row['count']
            ret.append((facet,row['term']))
        
    return ret

if __name__ == '__main__':
    op = OptionParser()
    op.add_option('-s','--start',
                  dest='start',
                  help='start date (inclusive)')
    op.add_option('-e','--end',
                  dest='end',
                  help='end date (exclusive)')
    op.add_option('-S','--size',
                  dest='size',
                  default=10,
                  help='num of term in facet')
    (opts,args) = op.parse_args()
    if not opts.start:
        sys.stderr.write("missing --start\n")
        sys.exit(1)

    if not opts.end:
        sys.stderr.write("missing --end\n")
        sys.exit(1)

    st = datetime.strptime(opts.start,'%Y-%m-%d')
    et = datetime.strptime(opts.end,'%Y-%m-%d')
    term_facet(date_filter=[st,et],size=opts.size)
