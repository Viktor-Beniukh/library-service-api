# Generated by Django 4.1.7 on 2023-02-28 19:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("borrowing", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="borrowing",
            name="borrow_date",
            field=models.DateField(),
        ),
    ]
