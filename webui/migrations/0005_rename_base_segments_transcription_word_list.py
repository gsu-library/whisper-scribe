# Generated by Django 5.1.1 on 2024-10-14 19:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webui', '0004_remove_transcription_model'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transcription',
            old_name='base_segments',
            new_name='word_list',
        ),
    ]
