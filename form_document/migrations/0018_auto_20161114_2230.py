# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-11-14 11:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form_document', '0017_auto_20161114_2227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formdocumentresponse',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'Hidden'), (1, 'Unopen'), (5, 'Abandoned'), (2, 'Opened'), (3, 'Saved'), (4, 'Received'), (6, 'Auto Saved'), (7, 'Edited')], default=1),
        ),
    ]
