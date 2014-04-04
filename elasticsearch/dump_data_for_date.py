#!/usr/bin/env python
"""
dump elasticsearch data to json based on date
"""
from pyes.es import ES
from pyes.query import MatchAllQuery,FilteredQuery
from pyes.filters import RangeFilter
from pyes.utils import ESRange
from datetime import date,timedelta,datetime
import jsonlib2 as json
import shutil,os,sys,gzip
from optparse import OptionParser

def dump(start,end,backupdir,eshost):
    conn = ES(eshost)
    out = file('/tmp/out.json','w')
    _type = 'habakkuk'
    q = MatchAllQuery()
    q = FilteredQuery(q, RangeFilter(qrange=ESRange('created_at_date',start,end,include_upper=False)))
    q = q.search()
    # print json.dumps(json.loads(q.to_search_json()),indent=2)
    resultset = conn.search(query=q,indices=_type+"-*", doc_types=[_type], scan=True)
    cnt=0
    if not resultset.total:
        sys.stderr.write("no data for %s - %s\n"%(start,end))
        return

    try:
        sys.stderr.write("Will write %d lines to %s\n"%(resultset.total, out.name))
        while True:
            r = resultset.next()
            cnt+=1
            out.write(json.dumps(r)+'\n')
    except StopIteration:
        pass

    out.close()

    # gzip
    ext = datetime.strftime(start,'%Y-%m-%d')
    backup = os.path.join(backupdir,"habakkuk-%s.json.gz"%ext)

    f_in = open(out.name,'rb')
    f_out = gzip.open(backup,'wb')
    f_out.writelines(f_in)
    f_out.close()
    f_out.close()
    sys.stderr.write("Created %s\n"%backup)

def main(start,end,opts):
    print start, end
    st = start
    et = start+timedelta(days=1)
    while st < end:
        dump(st,et,opts.outdir,opts.eshost)
        st = et
        et = et+timedelta(days=1)
    
if __name__=='__main__':
    op = OptionParser()
    op.add_option('-s','--start',
                  dest='start',
                  help='start date (inclusive)')
    op.add_option('-e','--end',
                  dest='end',
                  help='end date (exclusive)')
    op.add_option('-o','--outdir',
                  dest='outdir',
                  help='output directory',
                  default='./json')
    op.add_option('-H','--eshost',
                  dest='eshost',
                  help='host:port for elasticsearch',
                  default='localhost:9201')
    (opts,args) = op.parse_args()
    if not opts.start:
        sys.stderr.write("missing --start\n")
        sys.exit(1)
    st = datetime.strptime(opts.start,'%Y-%m-%d')

    if not opts.end:
        et = st+timedelta(days=1)
    else:
        et = datetime.strptime(opts.end,'%Y-%m-%d')

    if not os.path.exists(opts.outdir):
        sys.stderr.write("creating '%s'\n"%opts.outdir)
        os.mkdir(opts.outdir)

    main(st,et,opts)
