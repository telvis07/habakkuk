"""Script to generate dictionary mapping from
book -> index, bibleverse -> index.
Add a fake 'count' so the files can serve as dictionaries
for mahout clusterdump"""
from optparse import OptionParser
import xml.etree.ElementTree as ET
import re, sys
import cStringIO

def _normalize_book(book):
    # old func that reads newline delimited book
    # names
    if book=='psalms':
        book='psalm'
    if re.match("^[123]",book):
        # change 1 John into i john
        num, name = book.split(" ",1)
        book = "%s %s"%('i'*int(num), name)
    # change spaces to underscores
    return re.sub("[ ]","_",book)

def normalize_book(input):
#    generate id[TAB]book name
    for i, line in enumerate(file(input)):
        book = line.strip().lower()
        book = _normalize_book(book)
        print "\t".join([str(i+1),book])

def normalize_book_xml(input):
    # generate dictionary for bible books
    output = cStringIO.StringIO()
    root = ET.parse(input).getroot()
    books = root.getiterator('book')
    index = 1
    for child in books:
        book = child.attrib['name'].strip().lower()
        book = _normalize_book(book)
        # mahout dictionary expects term DocFreq Index
        # so just set DocFreq to '1'
        output.write("\t".join([book, '1', str(index)])+'\n')
        index+=1
    print index
    print output.getvalue()

def normalize_verse(input):
    # generate dictionary for bible verses
    output = cStringIO.StringIO()
    root = ET.parse(input).getroot()
    books = root.getiterator('book')
    index = 1
    for book_element in books:
        book = book_element.attrib['name'].strip().lower()
        book = _normalize_book(book)
        for chapter_element in book_element.getiterator('chapter'):
            chapnum = chapter_element.attrib['name']
            for verse_element in chapter_element.getiterator('verse'):
                vernum = verse_element.attrib['name']
                _verse = "%s:%s"%(chapnum,vernum)
                bibleverse =  " ".join([book,_verse])
                # print "\t".join([str(index),bibleverse])
                output.write("\t".join([bibleverse, '1', str(index)])+'\n')
                index+=1
    print index
    print output.getvalue()

if __name__== '__main__':
    op = OptionParser() 
    op.add_option('-f','--file',dest='infile',
                  help='load data/bible_book_list.txt and print info')
    op.add_option('--verse',
                  dest='do_verse',
                  action='store_true',
                  default=False,
                  help='load bible and verse from xml')
    (options,args) = op.parse_args()

    if not options.infile:
        options.infile = 'data/bible_book_list.txt'

    if options.infile.endswith('xml'):
        if options.do_verse:
            normalize_verse(options.infile)
        else:
            normalize_book_xml(options.infile)
    else:
        normalize_book(options.infile)
