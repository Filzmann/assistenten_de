# Generated by Django 3.1.7 on 2021-03-28 09:17

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('assistenten', '0003_assistent_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assistent',
            name='einstellungsdatum',
            field=models.DateTimeField(default=datetime.datetime(2021, 3, 28, 9, 17, 24, 885004, tzinfo=utc)),
        ),
    ]