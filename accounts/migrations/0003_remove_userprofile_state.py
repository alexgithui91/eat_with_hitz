# Generated by Django 3.2.5 on 2022-11-23 20:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20221123_1535'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='state',
        ),
    ]