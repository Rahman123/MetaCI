# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-05-30 22:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
        ('cumulusci', '0007_scratchorginstance_expiration_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='org',
            name='management_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='protected_orgs', to='auth.Group'),
        ),
    ]
