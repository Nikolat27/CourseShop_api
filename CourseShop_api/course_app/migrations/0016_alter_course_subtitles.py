# Generated by Django 4.2.11 on 2024-06-11 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("course_app", "0015_subtitle_course_costly_course_level_course_subtitles"),
    ]

    operations = [
        migrations.AlterField(
            model_name="course",
            name="subtitles",
            field=models.ManyToManyField(to="course_app.subtitle"),
        ),
    ]
