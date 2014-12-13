__author__ = 'telvis'
"""
Bulk load a file to elasticsearch
"""
from pyes import ES
from optparse import OptionParser
import gzip
import jsonlib2 as json
import traceback, sys, os

def flush(conn, count):
    bulk_result = conn.force_bulk()
    print "Bulked %s or %s items"%(len(bulk_result['items']), count)

def main(fn, args):
    conn = ES(args.host, bulk_size=10*args.bulksize)
    if fn.endswith(".gz"):
        fp = gzip.open(fn)
    else:
        fp = open(fn)

    count = 0
    total = 0

    try:
        for line in fp:
            doc = json.loads(line.strip())
            if doc.get("_id"):
                _id = doc["_id"]
                del doc["_id"]
            else:
                _id = None

            conn.index(doc=doc,
                       index=args.index,
                       doc_type=args.doctype,
                       id=_id,
                       bulk=True)
            count+=1
            total+=1
            if count % args.bulksize == 0:
                flush(conn, count)
                count = 0
    except:
        print "traceback", "".join(traceback.format_exception(*sys.exc_info()))
        raise
    finally:
        fp.close()

    try:
        flush(conn, count)
        conn.refresh(args.index)
    except:
        pass

    print "Indexed %s docs total"%total

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-H", "--host", dest="host",
                        default="localhost:9201",
                        help="elasticsearch host"),
    parser.add_option("-i", "--infile", dest="infile",
                        # required=True,
                        help="file to load to ES")
    parser.add_option('-b','--bulk', dest='bulksize',
                        default=500,
                        help="size of bulk message")
    parser.add_option('--index',
                        default="habakkuk-test",
                        help="elasticsearch index")
    parser.add_option('--doctype',
                        default='habakkuk',
                        help="elasticsearch type")
    (args, _) = parser.parse_args()

    if os.path.isdir(args.infile):
        files = sorted([os.path.join(args.infile, fn) for fn in os.listdir(args.infile)])
    else:
        files = [args.infile]

    for fn in files:
        if os.path.isdir(fn):
            print "skipping directory",fn
            continue
        print "Loading",fn
        main(fn, args)
