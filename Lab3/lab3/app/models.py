from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, User
from django.db import models


class Tariff(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(max_length=500, verbose_name="Описание",)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(verbose_name="Фото", blank=True, null=True)

    price = models.IntegerField(verbose_name="Цена")
    ram = models.IntegerField(verbose_name="RAM")
    cpu = models.IntegerField(verbose_name="CPU")
    ssd = models.IntegerField(verbose_name="SSD")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"
        db_table = "tariffs"
        ordering = ("pk",)


class Forecastcloudprice(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален')
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Создатель", related_name='owner', null=True)
    moderator = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Модератор", related_name='moderator', blank=True,  null=True)

    # Поле пользователя
    days = models.IntegerField(blank=True, null=True)

    # Вычисляемое поле
    price = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "Прогноз №" + str(self.pk)

    class Meta:
        verbose_name = "Прогноз"
        verbose_name_plural = "Прогнозы"
        db_table = "forecastCloudPrices"
        ordering = ('-date_formation', )


class TariffForecastcloudprice(models.Model):
    pk = models.CompositePrimaryKey("tariff_id", "forecastCloudPrice_id")
    tariff = models.ForeignKey(Tariff, on_delete=models.DO_NOTHING)
    forecastCloudPrice = models.ForeignKey(Forecastcloudprice, on_delete=models.DO_NOTHING)
    
    # Поле м-м
    count = models.IntegerField(default=0)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "tariff_forecastCloudPrice"
        ordering = ('pk', )
