import pytz
import random
from datetime import timedelta

from django.conf import settings


LOCALE = "dk_DK"
TIMEZONE = pytz.timezone(settings.TIME_ZONE)
# Setting default locale (this is not documented or intended by factory_boy)
# Faker._DEFAULT_LOCALE = LOCALE


def date_before(date):
    return date - timedelta(days=random.randint(1, 4 * 365))


def date_after(date):
    return date + timedelta(days=random.randint(1, 4 * 365))
