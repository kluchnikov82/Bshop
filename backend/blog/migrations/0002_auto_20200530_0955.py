# Generated by Django 2.1.7 on 2020-05-30 06:55

import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='slug',
            field=models.CharField(max_length=255, unique=True, validators=[django.core.validators.RegexValidator(re.compile('^[-a-z0-9]+\\Z'), 'Разрешены только буквы английского алфавита в нижнем регистре, цифры, дефисы', 'invalid')], verbose_name='URL'),
        ),
    ]
