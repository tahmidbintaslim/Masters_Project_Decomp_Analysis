# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-08-10 14:01
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('rango', '0012_experiment_filenames'),
    ]

    operations = [
        migrations.AddField(
            model_name='filedetail',
            name='resultId',
            field=models.TextField(default=datetime.datetime(2017, 8, 10, 14, 1, 55, 688882, tzinfo=utc)),
            preserve_default=False,
        ),
    ]