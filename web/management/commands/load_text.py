__author__ = 'telvis'

from django.core.management.base import BaseCommand
from optparse import make_option
import logging
import sys
import xml.etree.ElementTree as ET

from bible_verse_matching.normalize_bible_verses import normalize_book_name
from web.models import BibleText

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """ load bible text into the database """
    option_list = BaseCommand.option_list + (
        make_option('-f', '--infile',
                    dest='infile',
                    help="input xml file containing bible verse text"),
        make_option('-t', '--translation',
                    dest='translation',
                    default='KJV',
                    help="Acronym for the bibletranslation. (e.g. KJV, NIV)"
        )
    )

    def handle(self, *args, **options):
        if not options.get('infile'):
            print "please provide -f or --infile bible_verse_matching/data/kjv.xml"
            sys.exit(1)
        load_bibletext_from_xml(options['infile'], options['translation'])

def load_bibletext_from_xml(infile, translation):
    """
    Read bibleverses from the xml file and create BibleText models
    """
    logger.info("loading file='%s' translation='%s'"%(infile, translation))
    root = ET.parse(infile).getroot()
    books = root.getiterator('book')
    verse_id = 0
    entries = []
    BibleText.objects.filter(translation=translation).delete()


    for book_element in books:
        book = book_element.attrib['name'].strip().lower()
        book = normalize_book_name(book)
        for chapter_element in book_element.getiterator('chapter'):
            chapnum = chapter_element.attrib['name']
            for verse_element in chapter_element.getiterator('verse'):
                vernum = verse_element.attrib['name']
                _verse = "%s:%s"%(chapnum,vernum)
                bibleverse =  " ".join([book,_verse])
                entries.append(BibleText(verse_id=verse_id,
                                         translation=translation,
                                         bibleverse=bibleverse,
                                         bibleverse_human = bibleverse,
                                         text = verse_element.text,
                                         ))
                verse_id+=1
                if (verse_id % 100) == 0:
                    BibleText.objects.bulk_create(entries)
                    del entries[0:len(entries)]
                    logger.info("Just finished '%s' %d"%(bibleverse, verse_id))

    if len(entries):
        BibleText.objects.bulk_create(entries)
        logger.info("Just finished '%s' %d"%(bibleverse, verse_id))
    logger.info("finished loading file='%s' translation='%s'"%(infile, translation))