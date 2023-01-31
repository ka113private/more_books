# Generated by Django 3.2.16 on 2023-01-31 20:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0009_auto_20230131_2113'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bookshelf',
            old_name='book_id',
            new_name='book',
        ),
        migrations.RenameField(
            model_name='bookshelf',
            old_name='user_id',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='booktag',
            old_name='book_id',
            new_name='book',
        ),
        migrations.RenameField(
            model_name='booktag',
            old_name='tag_id',
            new_name='tag',
        ),
        migrations.RenameField(
            model_name='favoritebook',
            old_name='book_id',
            new_name='book',
        ),
        migrations.RenameField(
            model_name='favoritebook',
            old_name='user_id',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='taglike',
            old_name='booktag_id',
            new_name='booktag',
        ),
        migrations.RenameField(
            model_name='taglike',
            old_name='user_id',
            new_name='user',
        ),
    ]
