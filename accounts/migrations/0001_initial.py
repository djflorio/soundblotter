# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-11 15:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='email address')),
                ('username', models.CharField(max_length=100, unique=True, verbose_name='username')),
                ('is_active', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('activation_key', models.CharField(max_length=40)),
                ('key_expires', models.DateTimeField(null=True)),
                ('pwreset_key', models.CharField(max_length=40, null=True)),
                ('pwreset', models.BooleanField(default=False)),
                ('pwreset_expires', models.DateTimeField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]