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
from argparse import ArgumentParser

def dump_habakkuk(start,
                  end,
                  backupdir,
                  eshost,
                  _type ='habakkuk',
                  indices="habakkuk-all"):

    conn = ES(eshost)
    out = file('/tmp/out.json','w')
    q = MatchAllQuery()
    q = FilteredQuery(q, RangeFilter(qrange=ESRange('created_at_date',start,end,include_upper=False)))
    q = q.search()
    resultset = conn.search(query=q,
                            indices=indices,
                            doc_types=[_type],
                            scan=True)
    cnt=0
    if not resultset.total:
        sys.stderr.write("no data for %s - %s\n"%(start,end))
        return

    try:
        sys.stderr.write("Will write %d lines to %s\n"%(resultset.total, out.name))
        while True:
            r = resultset.next()
            r['_id'] = r._meta.id
            cnt+=1
            out.write(json.dumps(r)+'\n')
    except StopIteration:
        pass

    out.close()

    # gzip
    ext = datetime.strftime(start, '%Y-%m-%d')
    backup = os.path.join(backupdir,"habakkuk-%s.json.gz"%ext)

    f_in = open(out.name,'rb')
    f_out = gzip.open(backup,'wb')
    f_out.writelines(f_in)
    f_out.close()
    f_out.close()
    sys.stderr.write("Created %s\n"%backup)


def dump_topics(backupdir,
                eshost,
                _type,
                indices="topics-all"):
    conn = ES(eshost)
    out = file('/tmp/out.json','w')
    q = MatchAllQuery()
    q = q.search()

    resultset = conn.search(query=q,indices=indices, doc_types=[_type], scan=True)
    cnt=0
    if not resultset.total:
        sys.stderr.write("no data\n")
        return

    try:
        sys.stderr.write("Will write %d lines to %s\n"%(resultset.total, out.name))
        while True:
            r = resultset.next()
            r['_id'] = r._meta.id
            cnt+=1
            out.write(json.dumps(r)+'\n')
    except StopIteration:
        pass

    out.close()

    # gzip
    backup = os.path.join(backupdir,"topics.{}.json.gz".format(_type))

    f_in = open(out.name,'rb')
    f_out = gzip.open(backup,'wb')
    f_out.writelines(f_in)
    f_out.close()
    f_out.close()
    sys.stderr.write("Created %s\n"%backup)

def habakkuk_main(args):
    if not args.start:
        sys.stderr.write("missing --start\n")
        sys.exit(1)
    start = datetime.strptime(args.start,'%Y-%m-%d')

    if not args.end:
        end = start+timedelta(days=1)
    else:
        end = datetime.strptime(args.end,'%Y-%m-%d')

    if not os.path.exists(args.outdir):
        sys.stderr.write("creating '%s'\n"%args.outdir)
        os.mkdir(args.outdir)

    # start writing data from the index to disk
    print start, end
    st = start
    et = start+timedelta(days=1)
    while st < end:
        dump_habakkuk(st,et,args.outdir,args.eshost)
        st = et
        et = et+timedelta(days=1)

def topics_main(args):
    if not os.path.exists(args.outdir):
        sys.stderr.write("creating '%s'\n"%args.outdir)
        os.mkdir(args.outdir)

    # start writing data from the index to disk
    dump_topics(args.outdir,
                args.eshost,
                args.estype,
                indices=args.esindex)


def parse_args():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest='command_name',
                                       help='sub-command help')

    parser_habakkuk = subparsers.add_parser('habakkuk',
                                            help='dump data from habakkuk index')
    parser_habakkuk.add_argument('-s','--start',
                  dest='start',
                  help='start date (inclusive)')
    parser_habakkuk.add_argument('-e','--end',
                  dest='end',
                  help='end date (exclusive)')
    parser_habakkuk.add_argument('-o','--outdir',
                  dest='outdir',
                  help='output directory',
                  default='./json')
    parser_habakkuk.add_argument('-H','--eshost',
                  dest='eshost',
                  help='host:port for elasticsearch',
                  default='localhost:9201')
    parser_habakkuk.add_argument('-t','--estype',
                  dest='estype',
                  default='habakkuk')
    parser_habakkuk.add_argument('-i','--esindex',
                  dest='esindex',
                  default='habakkuk-all')

    parser_topics = subparsers.add_parser('topics',
                                          help='dump data from habakkuk index')
    parser_topics.add_argument('-o','--outdir',
                  dest='outdir',
                  help='output directory',
                  default='./json')
    parser_topics.add_argument('-H','--eshost',
                  dest='eshost',
                  help='host:port for elasticsearch',
                  default='localhost:9201')
    parser_topics.add_argument('-t','--estype',
                  dest='estype')
    parser_topics.add_argument('-i','--esindex',
                  dest='esindex',
                  default='topics-all')

    return parser.parse_args()

if __name__=='__main__':
    args = parse_args()

    if args.command_name == 'habakkuk':
        habakkuk_main(args)
    elif args.command_name == 'topics':
        topics_main(args)
    else:
        print "No such command",args.command_name