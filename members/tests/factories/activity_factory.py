from datetime import date

import factory
from members.tests.factories.factory_helpers import TIMEZONE, LOCALE
from members.tests.factories.providers import DanishProvider, CodingPiratesProvider
from members.models import Activity
from members.tests.factories.union_factory import UnionFactory
from members.tests.factories.department_factory import DepartmentFactory
from factory import Faker, SubFactory, LazyAttribute
from factory.django import DjangoModelFactory
from members.tests.factories.factory_helpers import (
    date_after,
    date_before,
)


Faker.add_provider(DanishProvider, locale=LOCALE)
Faker.add_provider(CodingPiratesProvider, locale="dk_DK")
Faker._DEFAULT_LOCALE = "dk_DK"


class ActivityFactory(DjangoModelFactory):
    class Meta:
        model = Activity
        exclude = ("active", "today")

    # Helper fields
    active = Faker("boolean")
    today = date.today()

    union = SubFactory(UnionFactory)
    department = SubFactory(DepartmentFactory, union=factory.SelfAttribute("..union"))
    name = Faker("activity")
    open_hours = Faker("numerify", text="kl. ##:00-##:00")
    responsible_name = Faker("name")
    responsible_contact = Faker("email")
    placename = Faker("city_suffix")
    zipcode = Faker("zipcode")
    city = Faker("city")
    streetname = Faker("street_name")
    housenumber = Faker("building_number")
    floor = Faker("floor")
    door = Faker("door")
    dawa_id = Faker("uuid4")
    description = Faker("text")
    instructions = Faker("text")
    signup_closing = Faker("date_between", start_date="-100d", end_date="+100d")
    start_date = LazyAttribute(
        lambda d: date_before(d.today)
        if d.active
        else Faker("date_object").generate({})
    )
    end_date = LazyAttribute(
        lambda d: date_after(d.today) if d.active else date_before(d.today)
    )
    updated_dtm = Faker("date_time", tzinfo=TIMEZONE)
    open_invite = Faker("boolean")
    price_in_dkk = Faker("random_number", digits=4)
    max_participants = Faker("random_number")
    min_age = Faker("random_int", min=5, max=18)
    max_age = LazyAttribute(
        lambda a: a.min_age + Faker("random_int", min=10, max=80).generate({})
    )
    member_justified = Faker("boolean")
