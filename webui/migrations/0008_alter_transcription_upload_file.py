# Generated by Django 5.1.1 on 2024-10-24 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webui', '0007_alter_transcription_upload_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transcription',
            name='upload_file',
            field=models.FileField(max_length=255, upload_to=''),
        ),
    ]
