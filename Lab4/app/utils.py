import random
from datetime import timedelta

from faker import Faker

from app.models import User, Forecastcloudprice
from app.redis import session_storage

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


def get_draft_forecastCloudPrice(request):
    user = identity_user(request)

    if user is None or user.is_superuser:
        return None

    forecastCloudPrice = Forecastcloudprice.objects.filter(owner=user).filter(status=1).first()

    return forecastCloudPrice


def identity_user(request):
    session = get_session(request)

    if session is None or session not in session_storage:
        return None

    user_id = session_storage.get(session)
    user = User.objects.get(pk=user_id)

    return user


def get_session(request):
    # Пробуем авторизоваться по куке session_id
    if request.COOKIES.get("session_id"):
        return request.COOKIES.get("session_id")

    # Пробуем авторизоваться по заголовку Authorization
    if request.headers.get("Authorization"):
        return request.headers.get("Authorization").split(" ")[0]

    return None
