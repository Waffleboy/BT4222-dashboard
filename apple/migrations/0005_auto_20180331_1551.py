# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-03-31 07:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apple', '0004_auto_20180328_2010'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweet',
            name='resolved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='twitteruser',
            name='age',
            field=models.CharField(blank=True, default=None, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='twitteruser',
            name='gender',
            field=models.CharField(blank=True, default=None, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='twitteruser',
            name='interest',
            field=models.CharField(blank=True, default=None, max_length=250, null=True),
        ),
    ]
