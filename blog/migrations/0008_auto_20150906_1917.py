# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_auto_20150906_1420'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='media',
            options={'ordering': ['-pub_date'], 'verbose_name_plural': 'media'},
        ),
        migrations.AddField(
            model_name='media',
            name='pub_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='media',
            name='image',
            field=models.ImageField(upload_to='%Y/%m/%d'),
        ),
    ]
