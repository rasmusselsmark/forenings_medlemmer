from members.tests.factories.factory_helpers import TIMEZONE
from members.models import Volunteer
from members.tests.factories.person_factory import PersonFactory
from members.tests.factories.department_factory import DepartmentFactory
from factory import Faker, SubFactory, LazyAttribute
from factory.django import DjangoModelFactory
from members.tests.factories.factory_helpers import date_after


class VolunteerFactory(DjangoModelFactory):
    class Meta:
        model = Volunteer

    person = SubFactory(PersonFactory)
    department = SubFactory(DepartmentFactory)

    added = Faker("date_time", tzinfo=TIMEZONE)
    confirmed = LazyAttribute(lambda d: date_after(d.added))
    removed = LazyAttribute(lambda d: date_after(d.added))
