# Generated by Django 5.1.7 on 2025-04-17 11:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ShipOps', '0005_userrole_userprofile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='role',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserRole',
        ),
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]
