# Generated by Django 5.1.7 on 2025-04-17 07:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ShipsAuth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='user_obj',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='auth_profile', to=settings.AUTH_USER_MODEL),
        ),
    ]
