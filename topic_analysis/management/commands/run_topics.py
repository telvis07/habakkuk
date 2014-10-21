__author__ = 'telvis'

from django.core.management.base import BaseCommand
from optparse import make_option
from topic_analysis.main import main
from datetime import datetime

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-d', '--date',
                    dest='date',
                    help='End date to start analysis - format=YYYY-MM-DD',
                    default='2014-05-26'),
        make_option('-n', '--num_days',
                    dest='num_days',
                    help='number of days prior to the end_date for analysis',
                    type='int',
                    default=7)
    )

    def handle(self, *args, **options):
        main(datetime.strptime(options['date'], '%Y-%m-%d'), num_days=options['num_days'])


