# Generated by Django 3.1.4 on 2020-12-14 08:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('requirements', '0002_auto_20201212_1130'),
        ('events', '0004_auto_20201213_1534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='events',
            name='requirements',
            field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, to='requirements.requirements'),
        ),
    ]