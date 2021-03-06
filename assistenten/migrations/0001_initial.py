# Generated by Django 3.1.7 on 2021-03-25 11:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Adresse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bezeichner', models.CharField(max_length=30)),
                ('strasse', models.CharField(max_length=30)),
                ('hausnummer', models.CharField(max_length=8)),
                ('plz', models.CharField(max_length=5)),
                ('stadt', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='ASN',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kuerzel', models.CharField(max_length=30)),
                ('name', models.CharField(max_length=30)),
                ('vorname', models.CharField(max_length=30)),
                ('email', models.CharField(max_length=30)),
                ('einsatzbuero', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Assistent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('vorname', models.CharField(max_length=30)),
                ('email', models.CharField(max_length=30)),
                ('einstellungsdatum', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='EB',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('vorname', models.CharField(max_length=30)),
                ('email', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Lohn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('erfahrungsstufe', models.IntegerField()),
                ('gueltig_ab', models.DateTimeField()),
                ('eingruppierung', models.IntegerField()),
                ('grundlohn', models.DecimalField(decimal_places=4, max_digits=4)),
                ('nacht_zuschlag', models.DecimalField(decimal_places=4, max_digits=4)),
                ('samstag_zuschlag', models.DecimalField(decimal_places=4, max_digits=4)),
                ('sonntag_zuschlag', models.DecimalField(decimal_places=4, max_digits=4)),
                ('feiertag_zuschlag', models.DecimalField(decimal_places=4, max_digits=4)),
                ('wechselschicht_zuschlag', models.DecimalField(decimal_places=4, max_digits=4)),
                ('orga_zuschlag', models.DecimalField(decimal_places=4, max_digits=4)),
                ('ueberstunden_zuschlag', models.DecimalField(decimal_places=4, max_digits=4)),
                ('hl_abend_zuschlag', models.DecimalField(decimal_places=4, max_digits=4)),
                ('silvester_zuschlag', models.DecimalField(decimal_places=4, max_digits=4)),
            ],
        ),
        migrations.CreateModel(
            name='PFK',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('vorname', models.CharField(max_length=30)),
                ('email', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Weg',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entfernung', models.DecimalField(decimal_places=4, max_digits=4)),
                ('dauer_in_minuten', models.IntegerField()),
                ('adresse1_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='assistenten.adresse')),
                ('adresse2_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='assistenten.adresse')),
            ],
        ),
        migrations.CreateModel(
            name='Urlaub',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('beginn', models.DateTimeField()),
                ('ende', models.DateTimeField()),
                ('status', models.CharField(max_length=10)),
                ('assistent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assistenten.assistent')),
            ],
        ),
        migrations.CreateModel(
            name='SchichtTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('beginn', models.DateTimeField()),
                ('ende', models.DateTimeField()),
                ('bezeichner', models.CharField(max_length=30)),
                ('asn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assistenten.asn')),
            ],
        ),
        migrations.CreateModel(
            name='Schicht',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('beginn', models.DateTimeField()),
                ('ende', models.DateTimeField()),
                ('ist_kurzfristig', models.BooleanField()),
                ('ist_ausfallgeld', models.BooleanField()),
                ('ist_assistententreffen', models.BooleanField()),
                ('ist_pcg', models.BooleanField()),
                ('ist_schulung', models.BooleanField()),
                ('asn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assistenten.asn')),
                ('assistent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assistenten.assistent')),
                ('beginn_adresse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='assistenten.adresse')),
                ('ende_adresse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='assistenten.adresse')),
            ],
        ),
        migrations.CreateModel(
            name='FesteSchicht',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wochentag', models.CharField(max_length=10)),
                ('beginn', models.DateTimeField()),
                ('ende', models.DateTimeField()),
                ('asn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assistenten.asn')),
                ('assistent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assistenten.assistent')),
            ],
        ),
        migrations.CreateModel(
            name='Brutto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monat', models.DateTimeField()),
                ('bruttolohn', models.DecimalField(decimal_places=4, max_digits=4)),
                ('stunden_gesamt', models.DecimalField(decimal_places=4, max_digits=4)),
                ('assistent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assistenten.assistent')),
            ],
        ),
        migrations.CreateModel(
            name='AU',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('beginn', models.DateTimeField()),
                ('ende', models.DateTimeField()),
                ('assistent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assistenten.assistent')),
            ],
        ),
        migrations.CreateModel(
            name='AssociationAsAsn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fest_vertretung', models.CharField(max_length=50)),
                ('asn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assistenten.asn')),
                ('assistent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assistenten.assistent')),
            ],
        ),
        migrations.AddField(
            model_name='assistent',
            name='asn',
            field=models.ManyToManyField(through='assistenten.AssociationAsAsn', to='assistenten.ASN'),
        ),
        migrations.AddField(
            model_name='asn',
            name='einsatzbegleitung',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asn', to='assistenten.eb'),
        ),
        migrations.AddField(
            model_name='asn',
            name='pflegefachkraft',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asn', to='assistenten.pfk'),
        ),
        migrations.AddField(
            model_name='adresse',
            name='asn',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assistenten.asn'),
        ),
        migrations.AddField(
            model_name='adresse',
            name='assistent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assistenten.assistent'),
        ),
    ]
