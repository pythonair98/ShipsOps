# Generated by Django 5.1.7 on 2025-05-19 07:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ShipOps', '0015_useraction'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='actual_discharge_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contract',
            name='actual_load_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contract',
            name='amendment_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contract',
            name='approval_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contract',
            name='approved_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_contracts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='contract',
            name='category',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='contract',
            name='completion_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contract',
            name='contingency_plan',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contract',
            name='contract_number',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='contract',
            name='contract_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='contract',
            name='is_amended',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='contract',
            name='next_review_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contract',
            name='parent_contract',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='amendments', to='ShipOps.contract'),
        ),
        migrations.AddField(
            model_name='contract',
            name='performance_rating',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contract',
            name='reminder_days',
            field=models.IntegerField(default=7, help_text='Days before contract end to send reminder'),
        ),
        migrations.AddField(
            model_name='contract',
            name='risk_level',
            field=models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium', max_length=20),
        ),
        migrations.AddField(
            model_name='contract',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('pending_approval', 'Pending Approval'), ('approved', 'Approved'), ('active', 'Active'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('disputed', 'Disputed')], default='draft', max_length=30),
        ),
        migrations.AddField(
            model_name='contract',
            name='tags',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contract',
            name='version',
            field=models.IntegerField(default=1),
        ),
    ]
