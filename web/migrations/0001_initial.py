# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from django.db import models, migrations
import xml.etree.ElementTree as ET
from django.conf import settings
import os

from bible_verse_matching.normalize_bible_verses import normalize_book_name
logger = logging.getLogger(__name__)

def load_bibletext_from_xml(apps, schema_editor):
    """
    Read bibleverses from the xml file and create BibleText models
    """
    infile = os.path.join(settings.PROJECT_ROOT, 'bible_verse_matching/data/kjv.xml')
    translation='KJV'
    BibleText = apps.get_model("web", 'BibleText')

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
                if (verse_id % 1000) == 0:
                    BibleText.objects.bulk_create(entries)
                    del entries[0:len(entries)]

    if len(entries):
        BibleText.objects.bulk_create(entries)
    logger.info("finished loading file='%s' translation='%s'"%(infile, translation))


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BibleText',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('translation', models.CharField(max_length=64)),
                ('bibleverse', models.CharField(max_length=64)),
                ('bibleverse_human', models.CharField(max_length=64)),
                ('verse_id', models.PositiveIntegerField()),
                ('text', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RunPython(load_bibletext_from_xml)
    ]
