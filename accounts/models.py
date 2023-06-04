from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    '''拡張ユーザーモデル'''
    profile_image = models.ImageField(verbose_name='サムネイル画像', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'CustomUser'
