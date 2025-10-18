from django.db import models
from django.forms import model_to_dict
from django.utils import timezone

from django.contrib.auth.models import User


class Tariff(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Название")
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(blank=True, null=True, default='default.png')
    description = models.TextField(verbose_name="Описание")

    ram = models.IntegerField(verbose_name="RAM")
    cpu = models.IntegerField(verbose_name="CPU")
    ssd = models.IntegerField(verbose_name="SSD")
    price = models.IntegerField(verbose_name="Цена")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"
        db_table = "tariffs"
        ordering = ("pk",)


class Forecast(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален')
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(verbose_name="Дата создания", default=timezone.now)
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Пользователь", null=True, related_name='owner')
    moderator = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Модератор", null=True, related_name='moderator')

    days = models.IntegerField(blank=True, null=True)
    
    # Вычисляемое поле
    price = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "прогноз №" + str(self.pk)

    def get_tariffs(self):
        return [
            {
                **model_to_dict(item.tariff),
                'count': item.count,
            }
            for item in TariffForecast.objects.filter(forecast=self)
        ]

    class Meta:
        verbose_name = "прогноз"
        verbose_name_plural = "прогнозы"
        db_table = "forecasts"
        ordering = ('-date_formation',)


class TariffForecast(models.Model):
    pk = models.CompositePrimaryKey("tariff_id", "forecast_id")
    tariff = models.ForeignKey(Tariff, on_delete=models.DO_NOTHING)
    forecast = models.ForeignKey(Forecast, on_delete=models.DO_NOTHING)
    count = models.IntegerField(default=0)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "tariff_forecast"
        ordering = ('pk', )
