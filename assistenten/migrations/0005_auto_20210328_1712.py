# Generated by Django 3.1.7 on 2021-03-28 15:12

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('assistenten', '0004_auto_20210328_1117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assistent',
            name='einstellungsdatum',
            field=models.DateField(default=datetime.datetime(2021, 3, 28, 15, 12, 24, 295569, tzinfo=utc)),
        ),
    ]