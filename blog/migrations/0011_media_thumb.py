# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0010_remove_media_thumbnail'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='thumb',
            field=models.ImageField(default=2, upload_to='thumbs/%Y/%m/%d'),
            preserve_default=False,
        ),
    ]
