# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_media_thumb'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='image',
            field=models.ImageField(upload_to='uploads/%Y/%m/%d'),
        ),
    ]
