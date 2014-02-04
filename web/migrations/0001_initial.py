# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ClusterData'
        db.create_table(u'web_clusterdata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('range', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('ml_json', self.gf('django.db.models.fields.TextField')()),
            ('d3_dendogram_json', self.gf('django.db.models.fields.TextField')()),
            ('num_clusters', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'web', ['ClusterData'])

        # Adding unique constraint on 'ClusterData', fields ['date', 'range']
        db.create_unique(u'web_clusterdata', ['date', 'range'])

        # Adding model 'BibleText'
        db.create_table(u'web_bibletext', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('translation', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('bibleverse', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('bibleverse_human', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('verse_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'web', ['BibleText'])


    def backwards(self, orm):
        # Removing unique constraint on 'ClusterData', fields ['date', 'range']
        db.delete_unique(u'web_clusterdata', ['date', 'range'])

        # Deleting model 'ClusterData'
        db.delete_table(u'web_clusterdata')

        # Deleting model 'BibleText'
        db.delete_table(u'web_bibletext')


    models = {
        u'web.bibletext': {
            'Meta': {'object_name': 'BibleText'},
            'bibleverse': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'bibleverse_human': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'translation': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'verse_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'web.clusterdata': {
            'Meta': {'unique_together': "(('date', 'range'),)", 'object_name': 'ClusterData'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'd3_dendogram_json': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ml_json': ('django.db.models.fields.TextField', [], {}),
            'num_clusters': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'range': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['web']