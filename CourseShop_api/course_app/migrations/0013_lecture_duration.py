# Generated by Django 4.2.11 on 2024-06-11 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("course_app", "0012_enrollment_purchased_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="lecture",
            name="duration",
            field=models.FloatField(blank=True, null=True),
        ),
    ]
