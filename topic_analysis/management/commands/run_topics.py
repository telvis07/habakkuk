__author__ = 'telvis'

from django.core.management.base import BaseCommand
from topic_analysis.main import main

class Command(BaseCommand):
    option_list = BaseCommand.option_list + ()

    def handle(self, *args, **options):
        main()


