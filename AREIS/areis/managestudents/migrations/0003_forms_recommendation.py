# Generated by Django 5.1.1 on 2024-11-03 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('managestudents', '0002_alter_forms_options_remove_forms_content10_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='forms',
            name='recommendation',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]