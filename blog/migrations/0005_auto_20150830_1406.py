# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_auto_20150829_1715'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['title'], 'verbose_name_plural': 'categories'},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-pub_date']},
        ),
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='post',
            name='slug',
            field=models.SlugField(unique_for_date='pub_date'),
        ),
    ]
