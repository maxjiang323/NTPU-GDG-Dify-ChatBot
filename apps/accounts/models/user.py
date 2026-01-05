from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    自訂使用者模型
    繼承 AbstractUser,保留所有內建欄位並新增額外欄位
    """

    # 新增的自訂欄位
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='電話號碼'
    )

    avatar = models.URLField(
        blank=True,
        null=True,
        verbose_name='頭像網址'
    )

    bio = models.TextField(
        blank=True,
        max_length=500,
        verbose_name='個人簡介'
    )

    class Meta:
        verbose_name = '使用者'
        verbose_name_plural = '使用者'

    def __str__(self):
        return self.username