# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-15 22:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0003_branch_is_removed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='branch',
            name='deleted',
        ),
    ]