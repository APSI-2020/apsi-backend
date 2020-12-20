# Generated by Django 3.1.4 on 2020-12-19 19:59

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='title',
            field=models.CharField(choices=[('lic.', users.models.AcademicTitle['lic']), ('inż.', users.models.AcademicTitle['inz']), ('mgr.', users.models.AcademicTitle['mgr']), ('dr.', users.models.AcademicTitle['dr']), ('prof.', users.models.AcademicTitle['prof']), ('prof. inż.', users.models.AcademicTitle['prof_inz']), ('mgr inż.', users.models.AcademicTitle['mgr_inz']), ('dr inż.', users.models.AcademicTitle['dr_inz']), ('dr hab.', users.models.AcademicTitle['dr_hab']), ('dr hab. inż.', users.models.AcademicTitle['dr_hab_inz'])], max_length=32, null=True),
        ),
    ]