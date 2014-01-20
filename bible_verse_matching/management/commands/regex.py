#!/usr/bin/env python
"""
Command to control bible verse regexes
"""
from django.core.management.base import BaseCommand
from optparse import make_option
from bible_verse_matching.regex_generator import build_regex, test_regex
import sys,os

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--test',dest='do_test',action='store_true',default=False,
                    help='load data/test_regex.txt and test'),
        make_option('--build',dest='do_build',action='store_true',default=False,
                    help='load data/bible_book_list.txt and print regex'),
        make_option('-f','--file',dest='infile',
                    help='load data/bible_book_list.txt and print regex'),
        )


    def handle(self, *args, **options):
        fn = None
        if not options['infile']:
            if options['do_test']:
                fn = 'bible_verse_matching/data/test_regex.txt'
            else:
                fn = 'bible_verse_matching/data/bible_book_list.txt'

        if not fn or not os.path.isfile(fn):
            print "%s is not a file"%fn
            sys.exit(1)

        fp = open(fn,'r')

        if options['do_build']:
            build_regex(fp)
        elif options['do_test']:
            test_regex(fp)
        else:
            print "try -h option"
