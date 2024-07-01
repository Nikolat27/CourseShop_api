# Generated by Django 4.2.11 on 2024-06-11 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("course_app", "0017_alter_course_price"),
    ]

    operations = [
        migrations.AlterField(
            model_name="course",
            name="price",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="If you did set the 'costly' field False, Do Not touch this field pls",
                max_digits=10,
                null=True,
            ),
        ),
    ]