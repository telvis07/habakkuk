from django.db import models
import logging
logger = logging.getLogger(__name__)


class BibleText(models.Model):
    translation = models.CharField(max_length=64, blank=False, null=False)
    bibleverse = models.CharField(max_length=64, blank=False, null=False)
    bibleverse_human = models.CharField(max_length=64, blank=False, null=False)
    verse_id = models.PositiveIntegerField()
    text = models.TextField(blank=False, null=False)

    def __unicode__(self):
        return "<bibleverse(%s) translation(%s)>"%(self.bibleverse, self.translation)