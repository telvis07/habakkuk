__author__ = 'telvis'
"""
Bulk load a file to elasticsearch
"""
from pyes import ES
from argparse import ArgumentParser
import gzip
import jsonlib2 as json
import traceback, sys

def flush(conn, count):
    bulk_result = conn.force_bulk()
    print "Bulked %s or %s items"%(len(bulk_result['items']), count)

def main(args):
    conn = ES(args.host, bulk_size=10*args.bulksize)
    if args.infile.endswith(".gz"):
        fp = gzip.open(args.infile)
    else:
        fp = open(args.infile)

    count = 0
    total = 0

    try:
        for line in fp:
            doc = json.loads(line.strip())
            conn.index(doc=doc, index=args.index, doc_type=args.doctype, bulk=True)
            count+=1
            total+=1
            if count % args.bulksize == 0:
                flush(conn, count)
                count = 0
    except:
        print "traceback", "".join(traceback.format_exception(sys.exc_info()))
    finally:
        fp.close()

    try:
        flush(conn, count)
        conn.refresh(args.index)
    except:
        pass

    print "Indexed %s docs total"%total

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-H", "--host", dest="host",
                        default="localhost:9201",
                        help="elasticsearch host"),
    parser.add_argument("-i", "--infile", dest="infile",
                        required=True,
                        help="file to load to ES")
    parser.add_argument('-b','--bulk', dest='bulksize',
                        default=500,
                        help="size of bulk message")
    parser.add_argument('--index',
                        default="habakkuk-test",
                        help="elasticsearch index")
    parser.add_argument('--doctype',
                        default='habakkuk',
                        help="elasticsearch type")
    args = parser.parse_args()
    main(args)