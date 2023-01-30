# Generated by Django 3.2.16 on 2023-01-27 09:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0007_alter_booktag_book_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booktag',
            name='book_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='booktags', to='books.book', verbose_name='書籍ID'),
        ),
    ]
