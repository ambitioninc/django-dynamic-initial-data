# Generated by Django 2.2.8 on 2020-02-19 20:16

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('dynamic_initial_data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreationReceipt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_attributes', django.contrib.postgres.fields.jsonb.JSONField()),
                ('model_class_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
        ),
    ]
