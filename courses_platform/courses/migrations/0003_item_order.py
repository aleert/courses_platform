# Generated by Django 2.2.2 on 2019-06-24 19:32

import courses.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_auto_20190624_1656'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='order',
            field=courses.fields.OrderField(default=1),
            preserve_default=False,
        ),
    ]
