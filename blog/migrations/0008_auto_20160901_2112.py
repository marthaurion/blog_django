# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-02 02:12
from __future__ import unicode_literals

from django.db import migrations
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_auto_20160828_1958'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='scale_image',
            field=versatileimagefield.fields.VersatileImageField(editable=False, max_length=200, null=True, upload_to='scale/%Y/%m/%d'),
        ),
    ]
