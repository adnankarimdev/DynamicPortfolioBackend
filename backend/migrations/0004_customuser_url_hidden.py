# Generated by Django 5.1 on 2024-11-20 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0003_customuser_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="url_hidden",
            field=models.BooleanField(default=False),
        ),
    ]