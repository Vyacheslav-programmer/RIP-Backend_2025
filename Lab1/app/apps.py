from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_ram = 'django.db.models.BigAutoRam'
    name = 'app'
    verbose_name = "Оценка стоимости облачного хостинга для веб-проекта"
