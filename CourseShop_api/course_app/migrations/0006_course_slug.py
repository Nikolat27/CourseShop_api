# Generated by Django 4.2.11 on 2024-06-07 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("course_app", "0005_rename_language_course_language"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="slug",
            field=models.SlugField(
                allow_unicode=True, blank=True, null=True, unique=True
            ),
        ),
    ]