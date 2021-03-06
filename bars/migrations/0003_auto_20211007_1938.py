# Generated by Django 3.2.7 on 2021-10-07 17:38

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bars', '0002_alter_schedule_bar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='zip_code',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1000, message='Un code postal Belge doit être plus grand ou égal à 1000'), django.core.validators.MaxValueValidator(9999, message='Un code postal Belge doit être plus grand ou égal à 1000')]),
        ),
        migrations.AlterField(
            model_name='bar',
            name='has_table_games',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='bar',
            name='has_video_games',
            field=models.BooleanField(default=False),
        ),
    ]
