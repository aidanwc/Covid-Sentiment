# Generated by Django 3.0.2 on 2020-05-19 01:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DailyScore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now=True)),
                ('dateTime', models.DateTimeField(auto_now=True)),
                ('score', models.FloatField()),
            ],
        ),
    ]
