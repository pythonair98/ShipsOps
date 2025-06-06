# Generated by Django 5.1.7 on 2025-05-17 12:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ShipOps', '0012_contract_created_by_contract_updated_by_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(choices=[('create', 'Create'), ('update', 'Update'), ('delete', 'Delete'), ('view', 'View'), ('login', 'Login'), ('logout', 'Logout'), ('export', 'Export'), ('import', 'Import'), ('other', 'Other')], max_length=20)),
                ('model_name', models.CharField(max_length=50)),
                ('object_id', models.CharField(blank=True, max_length=50, null=True)),
                ('details', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='actions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
                'indexes': [models.Index(fields=['user', 'action_type', 'timestamp'], name='ShipOps_use_user_id_6ec2a0_idx'), models.Index(fields=['model_name', 'object_id'], name='ShipOps_use_model_n_4d483f_idx')],
            },
        ),
    ]
