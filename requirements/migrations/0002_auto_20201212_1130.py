# Generated by Django 3.1.4 on 2020-12-12 11:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('requirements', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='requirements',
            old_name='requirementJson',
            new_name='requirement_json',
        ),
    ]
