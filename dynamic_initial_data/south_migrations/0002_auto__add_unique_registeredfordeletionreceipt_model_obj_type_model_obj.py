# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'RegisteredForDeletionReceipt', fields ['model_obj_type', 'model_obj_id']
        db.create_unique(u'dynamic_initial_data_registeredfordeletionreceipt', ['model_obj_type_id', 'model_obj_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'RegisteredForDeletionReceipt', fields ['model_obj_type', 'model_obj_id']
        db.delete_unique(u'dynamic_initial_data_registeredfordeletionreceipt', ['model_obj_type_id', 'model_obj_id'])


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'dynamic_initial_data.registeredfordeletionreceipt': {
            'Meta': {'unique_together': "(('model_obj_type', 'model_obj_id'),)", 'object_name': 'RegisteredForDeletionReceipt'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model_obj_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'model_obj_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'register_time': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['dynamic_initial_data']