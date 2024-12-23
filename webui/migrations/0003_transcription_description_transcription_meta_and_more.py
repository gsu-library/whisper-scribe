# Generated by Django 5.1.1 on 2024-10-14 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webui', '0002_alter_segment_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='transcription',
            name='description',
            field=models.TextField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='transcription',
            name='meta',
            field=models.JSONField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='transcription',
            name='notes',
            field=models.TextField(default=None, null=True),
        ),
    ]
