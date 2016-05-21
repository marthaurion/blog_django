# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-05-20 22:04
from __future__ import unicode_literals

from django.db import migrations, models
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_auto_20160201_1926'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='thumb',
            field=models.ImageField(blank=True, null=True, upload_to=b'thumb/%Y/%m/%d'),
        ),
        migrations.AlterField(
            model_name='media',
            name='full_image',
            field=versatileimagefield.fields.VersatileImageField(upload_to=b'%Y/%m/%d'),
        ),
    ]