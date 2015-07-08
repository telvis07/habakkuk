#!/usr/bin/env python
"""
Script to generate a Python regular expression for Bible
references. The output for --build is find_all_scriptures.py. 
The --test option tests the regex against known data
"""
import sys
import re
import os
from optparse import OptionParser
import jsonlib2 as json
#TODO: XXX
#Documentation
#Handle: eph. 6:1-3
#Causes false positive "deuteronomy 31 {STRING: 'december 31"

output_py = \
"""
# autogenerated by regex.py
import re

find_all_scriptures = re.compile(\"\"\"
%s
\"\"\",re.VERBOSE|re.MULTILINE).finditer

def filtergroupdict(ma):
    \"\"\"Remove all entries with values == None\"\"\"
    di = filter(lambda x: x[1]!=None and x[0]!='verse', ma.groupdict().items())

    if len(di) != 1:
        return None

    ret = {}
    ret['book'] = di[0][0]
    ret['verse'] = ma.groupdict()['verse']
    ret['verse'] = ret['verse'].replace(' ','')
    return ret

"""

def find_prefixes(fp,verbose=False):
    """
    return num, name, regex
    """
    prefix_map = {}
    book_map = {}
    book_order = []
    for line in fp:
        prefixlen = 3
        book = line.strip().lower()
        book_order.append(book)

        if re.match("^[123]",book):
            num, name = book.split(" ")
            namelen = len(name)
            if namelen <= prefixlen:
                prefixlen = namelen-1
            prefix = "%s %s"%(num, name[:prefixlen])
        else:
            name = book
            namelen = len(name)
            if namelen <= prefixlen:
                prefixlen = namelen-1
            prefix = name[:prefixlen]

        if prefix in prefix_map:
            if verbose: print "(%s,%s) prefix already in map for %s"%(prefix,book,prefix_map[prefix])
            for i in range(prefixlen, min([len(book),len(prefix_map[prefix])])+1):
                if book[:i] != prefix_map[prefix][:i]:
                    prefix_1 = book[:i]
                    prefix_map[prefix_1] = book
                    book_map[book] = prefix_1
                    prefix_2 = prefix_map[prefix][:i]
                    prefix_map[prefix_2] = prefix_map[prefix]
                    book_map[prefix_map[prefix_2]] = prefix_2
                    del prefix_map[prefix]
                    if verbose: print "Prefix len: %d works (%s,%s), (%s,%s)"%(i,prefix_1,prefix_map[prefix_1],prefix_2,prefix_map[prefix_2])
                    break
        else:
            prefix_map[prefix] = book
            book_map[book] = prefix

    prefix_li = []
    for book in book_order:
        if re.match("^[123]",book):
            num, name = book_map[book].split(" ")
            prefixlen = len(name)
        else:
            prefixlen = len(book_map[book])
        if verbose: print book, book_map[book], prefixlen
        prefix_li.append((book, prefixlen))
    return prefix_li

def build_regex(fp,verbose=False):
    # For each book in the bible
    # get name length
    # map {book_lower_case: book_lower_case{:3}\w{1,namelen-3}}
    # special case for 1st or 2nd books
    # check regex against book
    # build compound regex with all titles
    regex_map = {}
    regex_items = []
    prefixes = find_prefixes(fp)

    for book, prefixlen in prefixes:
        if verbose: print "book=%s,prefixlen=%d"%(book,prefixlen)

        if re.match("^[123]",book):
            num, name = book.split(" ")
            namelen = len(name)
            regex =  "%s\s*%s\\w{0,%d}\.?"%(num,name[:prefixlen],namelen-prefixlen)
            regex += "|%s\s+%s\\w{0,%d}"%('i'*int(num),name[:prefixlen],namelen-prefixlen)
        else:
            name = book
            namelen = len(name)
            num=0
            if book == "song of solomon":
                regex = "%s[\\w\\s]{0,%d}"%(name[:prefixlen],namelen-prefixlen)
            else:
                regex = "%s\\w{0,%d}"%(name[:prefixlen],namelen-prefixlen)

        # mogrify book name for regular expression group name
        _book = book
        if num:
            _book = "%s %s"%('i'*int(num), name)
        _book = re.sub("[ ]","_",_book)

        # regex_map[book]=regex
        regex="(?P<%s>%s\.?)"%(_book,regex)
        regex_map[book]=regex
        regex_items.append((book,regex))
        print 'val genesis_re = start_pattern.concat("""(gen\w{0,4}\.?)\s+""").concat(verse_pattern).r'%book,regex
        
        #print "%s (%s)"%(regex_map[book],book)
        ma = re.search(regex_map[book], book)
        if not ma:
            print "regex failed for %s, '%s'"%(book, regex_map[book])
            sys.exit(1)

    build = "\n|".join(map(lambda x: "%-20s %-20s"%(x[1],"# "+x[0]),regex_items))
    # NOTICE: Causes false positive "deuteronomy 31 {STRING: 'december 31"
    # build = "(\n%s\n)\n\s+(?P<verse>\d{1,3}:\d{1,3}|\w+ \d{1,3})"%build
    build = "(\n%s\n)\n\s+(?P<verse>\d{1,3}\s*:\s*\d{1,3})"%build
    out = file('find_all_scriptures.py','w')
    out.write(output_py%build)
    out.close()
    print "Wrote",out.name
    for book in regex_map:
        ma = re.search(build, book+" 1:1", re.VERBOSE)
        if not ma:
            print "build regex failed for %s, '%s'"%(book,regex_map[book])
            # sys.exit(1)
        # print ma.group('book'),ma.group('verse')


def build_scala_regex(fp,verbose=False):
    # For each book in the bible
    # get name length
    # map {book_lower_case: book_lower_case{:3}\w{1,namelen-3}}
    # special case for 1st or 2nd books
    # check regex against book
    # build compound regex with all titles
    regex_map = {}
    regex_items = []
    prefixes = find_prefixes(fp)

    for book, prefixlen in prefixes:
        if verbose: print "book=%s,prefixlen=%d"%(book,prefixlen)

        if re.match("^[123]",book):
            num, name = book.split(" ")
            namelen = len(name)
            regex =  "%s\s*%s\\w{0,%d}\.?"%(num,name[:prefixlen],namelen-prefixlen)
            regex += "|%s\s+%s\\w{0,%d}"%('i'*int(num),name[:prefixlen],namelen-prefixlen)
        else:
            name = book
            namelen = len(name)
            num=0
            if book == "song of solomon":
                regex = "%s[\\w\\s]{0,%d}"%(name[:prefixlen],namelen-prefixlen)
            else:
                regex = "%s\\w{0,%d}"%(name[:prefixlen],namelen-prefixlen)

        # mogrify book name for regular expression group name
        _book = book
        if num:
            _book = "%s %s"%('i'*int(num), name)
        _book = re.sub("[ ]","_",_book)

        # regex_map[book]=regex
        # regex="(?P<%s>%s\.?)"%(_book,regex)
        # regex_map[book]=regex
        # regex_items.append((book,regex))
        #print 'val {book}_re =\n  start_pattern.concat("""({regex}\.?)""").concat(verse_pattern).r.unanchored'.format(book=_book,regex=regex)
        print 'case {_book}_re(ma_text, verse) => \n  Map("book" -> "{_book}", "verse" -> verse.replace(" ",""), "ma_text" -> ma_text)'.format(_book=_book,book=book)



def test_regex(fp,verbose=True):
    """ Read test lines from file. Should be inputstring,expected regex groupname.
    If no expected regex group name is found then keep going """
    from find_all_scriptures import find_all_scriptures, filtergroupdict
    print "Reading",fp.name
    i=0
    found_books = set()
    for line in fp:
        found = False
        line=line.strip().lower()
        if line.find(',') != -1:
            line,answer = line.split(',')
        else:
            answer = None
        matches = find_all_scriptures(line)
        for ma in matches:
            #print ma.groups()
            #print ma.groupdict()
            #print ma.lastgroup
            #print ma.lastindex
            ret =  filtergroupdict(ma)
            if answer and ret['book']+" "+ret['verse'] != answer:
                print "%s matched wrong regex %s, should be=%s"%(line,ret['book'],answer)
                sys.exit(1)
            if verbose: print "%s,%s %s"%(line, ret['book'],ret['verse'])
            found_books.add(ret['book'])
            found = True
        if not found and answer:
            print "Failed to match ",line,found,answer
            sys.exit(1)

    print "Found %d distinct books"%len(found_books)

def fix_results(fn, outputdir='/tmp/', show_misses=True):
    """ Assumes the caller has generated a new regex and wants to fix the
    results captured with the old regex. Read a JSON results file containing
    tweets captured by habakkuk and show any line does not match. """
    from find_all_scriptures import find_all_scriptures, filtergroupdict
    import gzip, copy, traceback

    fp = None
    found_match_cnt = 0
    miss_match_cnt = 0

    if fn.endswith('gz'):
        fp = gzip.open(fn)
        found_match_fp = gzip.open(os.path.join(outputdir, os.path.basename(fn)),'w')
    else:
        fp = open(fn)
        found_match_fp = open(os.path.join(outputdir, os.path.basename(fn)),'w')

    bv_set = set([line.strip() for line in open('./analysis/join_data/bibleverses.txt')])

    print "Reading",fn
    print "Writing fixed file to",found_match_fp.name
    print ""

    try:
        for line in fp:
            res = json.loads(line)
            txt = res['text'].lower()
            matches = [ma for ma in find_all_scriptures(txt)]

            if len(matches) is 0 or res['bibleverse'] not in bv_set:
                miss_match_cnt+=1
                if show_misses:
                    print "missed",line
            else:
                found_match_fp.write(line)
                found_match_cnt+=1
                ret = filtergroupdict(ma)
                newres = copy.deepcopy(res)
                newres['matext'] = ma.string[ma.start():ma.end()].replace('\r\n',' ') #actual matched string
                newres['book'] = ret['book']
                newres['bibleverse'] = " ".join((ret['book'],ret['verse']))
                if newres['bibleverse'] != res['bibleverse']:
                    print "Matched verse changed from %s to %s - text '%s'\n"%(res['bibleverse'],
                                                                             newres['bibleverse'],
                                                                             unicode(res['text']).encode('ascii',errors='ignore'))
    except Exception, ex:
        print "Failure!!!"
        print "line",line
        print "regex returned",ret
        print "traceback", "".join(traceback.format_exception(*sys.exc_info()))
    finally:
        fp.close()
        found_match_fp.close()
        print "closed",fn
        print "closed",found_match_fp.name
        print "# Misses",miss_match_cnt
        print "# Matches",found_match_cnt

if __name__=='__main__':
    op = OptionParser() 
    op.add_option('--test',dest='do_test',action='store_true',default=False,
                  help='load data/test_regex.txt and test')
    op.add_option('--build',dest='do_build',action='store_true',default=False,
                  help='load data/bible_book_list.txt and print regex')
    op.add_option('--scala',dest='do_scala',action='store_true',default=False,
                  help='load data/bible_book_list.txt and print scala regex and case')
    op.add_option('-f','--file',dest='infile',
                  help='load data/bible_book_list.txt and print regex')
    (options,args) = op.parse_args()

    if not options.infile:
        if options.do_test:
            options.infile = 'data/test_regex.txt'
        else:
            options.infile = 'data/bible_book_list.txt'

    if not os.path.isfile(options.infile):
        print "%s is not a file"%options.infile
        sys.exit(1)

    fp = open(options.infile,'r')

    if options.do_build:
        build_regex(fp)
    elif options.do_scala:
        build_scala_regex(fp)
    elif options.do_test:
        test_regex(fp)
    else:
        op.print_help()
