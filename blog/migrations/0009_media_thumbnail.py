# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_auto_20150906_1917'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='thumbnail',
            field=models.ImageField(editable=False, default=2, upload_to='thumbs/%Y/%m/%d'),
            preserve_default=False,
        ),
    ]
