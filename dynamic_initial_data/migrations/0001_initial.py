# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegisteredForDeletionReceipt',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('model_obj_id', models.PositiveIntegerField()),
                ('register_time', models.DateTimeField()),
                ('model_obj_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='registeredfordeletionreceipt',
            unique_together=set([('model_obj_type', 'model_obj_id')]),
        ),
    ]
