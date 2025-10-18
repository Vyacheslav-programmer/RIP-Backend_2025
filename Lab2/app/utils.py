import random
from datetime import timedelta
from faker import Faker

f = Faker("ru_RU")

def random_date(start_date="-1y", end_date="+1w"):
    return f.date_time_between(start_date=start_date, end_date=end_date)


def random_timedelta(factor=100):
    return timedelta(random.uniform(0, 1) * factor)


def random_bool():
    return f.boolean()


def random_text():
    return f.text()


def random_phone():
    return f.phone_number()
