# Generated by Django 3.2.16 on 2023-03-05 13:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0012_auto_20230216_0620'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='カテゴリ名')),
            ],
            options={
                'verbose_name_plural': 'Category',
            },
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='サブカテゴリ名')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.category', verbose_name='カテゴリ')),
            ],
            options={
                'verbose_name_plural': 'SubCategory',
            },
        ),
        migrations.AddField(
            model_name='book',
            name='sub_category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='books.subcategory', verbose_name='サブカテゴリ'),
            preserve_default=False,
        ),
    ]
