# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2018-01-24 21:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.migrations.operations.special
import django.utils.timezone
import pytz
from datetime import datetime


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    Waitinglist = apps.get_model("members", "Waitinglist")
    db_alias = schema_editor.connection.alias
    for waitinglistItem in Waitinglist.objects.all():
        waitinglistItem.on_waiting_list_since_new = waitinglistItem.person.added
        waitinglistItem.added_dtm_new = datetime(
            waitinglistItem.added_dtm.year,
            waitinglistItem.added_dtm.month,
            waitinglistItem.added_dtm.day,
            0,
            0,
            0,
            tzinfo=pytz.utc
        )
        waitinglistItem.save()


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0104_auto_20180120_0019'),
    ]

    operations = [
        migrations.AddField(
            model_name='waitinglist',
            name='added_dtm_new',
            field=models.DateTimeField(null=True, verbose_name='Tilføjet (midlertidig)'),
        ),
        migrations.AddField(
            model_name='waitinglist',
            name='on_waiting_list_since_new',
            field=models.DateTimeField(null=True, verbose_name='Venteliste position (midlertidig)'),
        ),
        migrations.RunPython(
            code=forwards_func,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RemoveField(
            model_name='waitinglist',
            name='added_dtm',
        ),
        migrations.RemoveField(
            model_name='waitinglist',
            name='on_waiting_list_since',
        ),
        migrations.RenameField(
            model_name='waitinglist',
            old_name='added_dtm_new',
            new_name='added_dtm',
        ),
        migrations.RenameField(
            model_name='waitinglist',
            old_name='on_waiting_list_since_new',
            new_name='on_waiting_list_since',
        ),
        migrations.AlterField(
            model_name='waitinglist',
            name='added_dtm',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Tilføjet'),
        ),
        migrations.AlterField(
            model_name='waitinglist',
            name='on_waiting_list_since',
            field=models.DateTimeField(verbose_name='Venteliste position'),
        ),
    ]
