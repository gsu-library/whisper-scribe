# Generated by Django 5.1.1 on 2024-09-24 17:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Transcription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('upload_file', models.FileField(upload_to='webui/files/uploads/')),
                ('model', models.CharField(max_length=255)),
                ('base_segments', models.JSONField(default=None, null=True)),
                ('diarization', models.JSONField(default=None, null=True)),
                ('submitted', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Segment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.FloatField()),
                ('end', models.FloatField()),
                ('text', models.TextField()),
                ('speaker', models.CharField(default='', max_length=255)),
                ('probability', models.FloatField(default=None, null=True)),
                ('transcription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webui.transcription')),
            ],
        ),
    ]
