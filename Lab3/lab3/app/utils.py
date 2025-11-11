import random
from datetime import timedelta

from django.contrib.auth.models import User
from faker import Faker

from app.models import Forecastcloudprice

f = Faker("ru_RU")

def random_date(start_date="-1y", end_date="+1w"):
    return f.date_time_between(start_date=start_date, end_date=end_date)


def random_timedelta(factor=100):
    return timedelta(random.uniform(0, 1) * factor)


def random_bool():
    return f.boolean()


def random_text():
    return f.sentence(nb_words=10)


def random_phone():
    return f.phone_number()


def get_draft_forecastCloudPrice():
    return Forecastcloudprice.objects.filter(status=1).first()


def get_user():
    return User.objects.filter(is_superuser=False).first()


def get_moderator():
    return User.objects.filter(is_superuser=True).first()


def identity_user(request):
    return get_user()

