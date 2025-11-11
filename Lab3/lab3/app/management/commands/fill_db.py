from django.core.management.base import BaseCommand

from app.calc import calc
from app.models import *
from app.serializers import ForecastcloudpriceSerializer
from app.utils import *


def add_users():
    User.objects.create_user("user", "user@user.com", "1234", first_name="user", last_name="user")
    User.objects.create_superuser("root", "root@root.com", "1234", first_name="root", last_name="root")

    for i in range(2, 10):
        User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234", first_name=f"user{i}", last_name=f"user{i}")
        User.objects.create_superuser(f"root{i}", f"root{i}@root.com", "1234", first_name=f"user{i}", last_name=f"user{i}")


def add_tariffs():
    Tariff.objects.create(
        name="AWS EC2",
        description="Amazon Elastic Compute Cloud — одна из инфраструктурных служб Amazon Web Services, позволяющая подписчику арендовать виртуальные выделенные серверы, называемые «экземплярами». Взаимодействовать со службой возможно с помощью веб-интерфейса, интерфейса командной строки, а также программно посредством API.",
        ram=16,
        cpu=4,
        ssd=40,
        price=1000,
        image="1.png"
    )

    Tariff.objects.create(
        name="Google Cloud",
        description="Google Cloud (GCP) — это облачная платформа от Google, которая предоставляет компаниям и разработчикам набор сервисов для работы с данными, вычислениями, хранением информации, аналитикой и машинным обучением.",
        ram=32,
        cpu=2,
        ssd=20,
        price=3000,
        image="2.png"
    )

    Tariff.objects.create(
        name="Azure Cloud",
        description="Azure Cloud (Microsoft Azure) — это постоянно расширяющийся набор облачных сервисов компании Microsoft, который предоставляет пользователям доступ к вычислительным ресурсам, хранилищу данных, сетевым решениям, аналитике и услугам искусственного интеллекта через Интернет",
        ram=16,
        cpu=8,
        ssd=10,
        price=2500,
        image="3.png"
    )

    Tariff.objects.create(
        name="Sber Cloud",
        description="Sber Cloud — это онлайн-сервис, позволяющий хранить ваши файлы (фото, видео, документы) и работать с ними удалённо, используя интернет с любого устройства.",
        ram=8,
        cpu=4,
        ssd=20,
        price=4000,
        image="4.png"
    )

    Tariff.objects.create(
        name="Yandex Cloud",
        description="Yandex Cloud — публичная облачная платформа, разработанная российской интернет-компанией Яндекс. Yandex Cloud предоставляет частным и корпоративным пользователям инфраструктуру и вычислительные ресурсы в формате «как услуга»",
        ram=16,
        cpu=2,
        ssd=32,
        price=1500,
        image="5.png"
    )

    Tariff.objects.create(
        name="VK Cloud",
        description="VK Cloud — это универсальная платформа облачных сервисов от VK, которая предоставляет компаниям и разработчикам доступ к вычислительным ресурсам, хранилищам, управляемым базам данных, контейнерам и другим услугам по модели «плати за потребление»",
        ram=32,
        cpu=8,
        ssd=32,
        price=1000,
        image="6.png"
    )


def add_forecastCloudPrices():
    users = User.objects.filter(is_staff=False)
    moderators = User.objects.filter(is_staff=True)
    tariffs = Tariff.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        owner = random.choice(users)
        add_forecastCloudPrice(status, tariffs, owner, moderators)

    # add_forecastCloudPrice(1, tariffs, users[0], moderators)
    add_forecastCloudPrice(2, tariffs, users[0], moderators)
    add_forecastCloudPrice(3, tariffs, users[0], moderators)
    add_forecastCloudPrice(4, tariffs, users[0], moderators)
    add_forecastCloudPrice(5, tariffs, users[0], moderators)

    for _ in range(10):
        status = random.randint(2, 5)
        add_forecastCloudPrice(status, tariffs, users[0], moderators)


def add_forecastCloudPrice(status, tariffs, owner, moderators):
    forecastCloudPrice = Forecastcloudprice.objects.create()
    forecastCloudPrice.status = status

    if status in [3, 4]:
        forecastCloudPrice.moderator = random.choice(moderators)
        forecastCloudPrice.date_complete = random_date()
        forecastCloudPrice.date_formation = forecastCloudPrice.date_complete - random_timedelta()
        forecastCloudPrice.date_created = forecastCloudPrice.date_formation - random_timedelta()
    else:
        forecastCloudPrice.date_formation = random_date()
        forecastCloudPrice.date_created = forecastCloudPrice.date_formation - random_timedelta()

    forecastCloudPrice.days = random.randint(1, 30)

    forecastCloudPrice.owner = owner

    for tariff in random.sample(list(tariffs), 3):
        item = TariffForecastcloudprice(
            forecastCloudPrice=forecastCloudPrice,
            tariff=tariff,
            count=random.randint(1, 10)
        )
        item.save()

    if status == 3:
        serializer = ForecastcloudpriceSerializer(forecastCloudPrice)
        forecastCloudPrice.price = calc(serializer.data)

    forecastCloudPrice.save()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_tariffs()
        add_forecastCloudPrices()
