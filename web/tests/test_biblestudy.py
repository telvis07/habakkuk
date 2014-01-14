__author__ = 'telvis'
from django.test import TestCase
import logging
from web.views import biblestudy
from mock import patch
logger = logging.getLogger(__name__)

class BibleStudyTest(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_basic(self):
        """ test the bible study view """
        with patch('web.search.get_scriptures_by_date',return_value=self.mock_result()):
            pass

    def mock_result(self):
        return [{"bibleverse":"John 3:16",
                 "text":"For God so loved the world that he gave his one and only Son,"
                  "that whoever believes in him shall not perish but have eternal life.",
                  "recommendations":["Book 1:1", "Book 1:2", "Book 1:3"]},
                  {"bibleverse":"1 John 4:19",
                  "text":"We love because he first loved us.",
                  "recommendations":["Book 2:1", "Book 2:2", "Book 2:3"]},
                  {"bibleverse":"1 Corinthians 13:4",
                  "text":"Love is patient, love is kind. It does not envy, it does not boast, it is not proud.",
                  "recommendations":["Book 2:1", "Book 2:2", "Book 2:3"]},
                  {"bibleverse":"1 Corinthians 13:13",
                  "text":"And now these three remain: faith, hope and love. But the greatest of these is love.",
                  "recommendations":["Book 2:1", "Book 2:2", "Book 2:3"]},
                  {"bibleverse":"Psalm 37:23",
                  "text":"The steps of a good man are ordered by the Lord: and he delighteth in his way.",
                  "recommendations":["Book 2:1", "Book 2:2", "Book 2:3"]},
                ]