# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-04-12 14:03
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apple', '0008_auto_20180407_1711'),
    ]

    operations = [
        migrations.AddField(
            model_name='twitteruser',
            name='following_ids',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
    ]
