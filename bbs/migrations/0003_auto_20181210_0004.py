# Generated by Django 2.1.2 on 2018-12-09 16:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bbs', '0002_auto_20181031_0008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='choice',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]