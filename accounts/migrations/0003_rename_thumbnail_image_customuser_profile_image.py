# Generated by Django 3.2.16 on 2023-01-29 13:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_customuser_thumbnail_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='thumbnail_image',
            new_name='profile_image',
        ),
    ]
