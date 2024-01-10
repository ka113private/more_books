# Generated by Django 3.2.16 on 2024-01-10 09:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('books', '0018_auto_20240104_1828'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inquiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='名前')),
                ('email', models.EmailField(max_length=254, verbose_name='メールアドレス')),
                ('title', models.CharField(max_length=30, verbose_name='問い合わせタイトル')),
                ('message', models.TextField(max_length=2000, verbose_name='問い合わせ内容')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ユーザー')),
            ],
            options={
                'verbose_name': 'Inquiry',
            },
        ),
    ]
