# Generated by Django 2.1.3 on 2019-07-02 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0005_auto_20190701_2049'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='visible',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='course',
            name='is_enroll_open',
            field=models.BooleanField(default=True),
        ),
    ]
