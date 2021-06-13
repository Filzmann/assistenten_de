# Generated by Django 3.1.8 on 2021-05-13 11:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assistenten', '0011_auto_20210510_0006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asn',
            name='einsatzbegleitung',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='asns', to='assistenten.eb'),
        ),
        migrations.AlterField(
            model_name='asn',
            name='pflegefachkraft',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='asns', to='assistenten.pfk'),
        ),
    ]