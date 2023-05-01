# Generated by Django 2.2.19 on 2023-04-30 21:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_auto_20230430_2056'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='reservation_unique',
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='unique_follow'),
        ),
    ]