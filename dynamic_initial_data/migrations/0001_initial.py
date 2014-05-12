# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'RegisteredForDeletionReceipt'
        db.create_table(u'dynamic_initial_data_registeredfordeletionreceipt', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('model_obj_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('model_obj_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('register_time', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'dynamic_initial_data', ['RegisteredForDeletionReceipt'])


    def backwards(self, orm):
        # Deleting model 'RegisteredForDeletionReceipt'
        db.delete_table(u'dynamic_initial_data_registeredfordeletionreceipt')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'dynamic_initial_data.registeredfordeletionreceipt': {
            'Meta': {'object_name': 'RegisteredForDeletionReceipt'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model_obj_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'model_obj_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'register_time': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['dynamic_initial_data']