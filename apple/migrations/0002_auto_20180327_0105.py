# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-03-26 17:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apple', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweet',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, default=None, max_digits=9, null=True),
        ),
        migrations.AlterField(
            model_name='tweet',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, default=None, max_digits=9, null=True),
        ),
    ]
