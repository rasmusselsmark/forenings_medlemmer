import os
import socket
from datetime import timedelta, date

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils import timezone
from factory import Faker
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from members.tests.factories import (
    DepartmentFactory,
    ActivityFactory,
    ActivityParticipantFactory,
    MemberFactory,
)
from members.tests.factories.factory_helpers import TIMEZONE
from members.tests.test_functional.functional_helpers import log_in

"""
This test goes to a department page

"""


class DepartmentTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())
    serialized_rollback = True

    def setUp(self):
        self.department = DepartmentFactory.create(
            name="Visiting department",
            created=(timezone.now() - timedelta(days=5)).date(),
            isVisible=True,
            closed_dtm=None,
        )
        self.other_department = DepartmentFactory.create(
            name="Other department",
            created=(timezone.now() - timedelta(days=5)).date(),
            isVisible=True,
            closed_dtm=None,
        )
        self.member = MemberFactory.create(department=self.department)

        past_date = date.today() + timedelta(days=-100)
        one_day = timedelta(days=1)
        self.activities = {}
        for dep in [self.department, self.other_department]:
            self.activities[dep.name] = {}
            for activity_type in [
                "ARRANGEMENT",
                "FORLØB",
                "FORENINGSMEDLEMSKAB",
                "STØTTEMEDLEMSKAB",
            ]:
                self.activities[dep.name][activity_type] = {}
                for open in [True, False]:
                    self.activities[dep.name][activity_type][open] = {}
                    for end_date in ["active", "historic"]:
                        self.activities[dep.name][activity_type][open][end_date] = {}
                        for variant in ["participate", "recent", "signup_due"]:
                            self.activities[dep.name][activity_type][open][end_date][
                                variant
                            ] = ActivityFactory.create(
                                open_invite=open,
                                min_age=5,
                                max_age=90,
                                department=dep,
                                signup_closing=(
                                    past_date
                                    if (
                                        variant == "signup_due"
                                        or end_date == "historic"
                                    )
                                    else past_date + timedelta(days=200)
                                ),
                                start_date=past_date + timedelta(days=-200),
                                end_date=(
                                    past_date + one_day
                                    if end_date == "historic"
                                    else Faker(
                                        "future_date", end_date="+100d", tzinfo=TIMEZONE
                                    )
                                ),
                                name=f"{dep}-{activity_type}-{open}-{end_date}-{variant}",
                                activitytype_id=activity_type,
                            )
                            if variant == "participate":
                                print(
                                    f"participating in {self.activities[dep.name][activity_type][open][end_date][variant]}"
                                )
                                ActivityParticipantFactory.create(
                                    activity=self.activities[dep.name][activity_type][
                                        open
                                    ][end_date][variant],
                                    member=self.member,
                                )
                            past_date += one_day + one_day

        self.browser = webdriver.Remote(
            "http://selenium:4444/wd/hub", DesiredCapabilities.CHROME
        )
        log_in(self, self.member.person)
        # Loads the department resource
        self.browser.get(f"{self.live_server_url}/departments/{self.department.name}")

    def tearDown(self):
        if not os.path.exists("test-screens"):
            os.mkdir("test-screens")
        self.browser.save_screenshot("test-screens/department_list_final.png")
        self.browser.quit()

    def test_department(self):
        self.assertIn(
            self.department.name,
            map(lambda e: e.text, self.browser.find_elements_by_xpath("//*")),
        )
        self.assertGreater(
            self.browser.page_source.index(self.department.responsible_name), 1
        )
        self.assertIn(
            f"mailto:{self.department.department_email}",
            map(
                lambda e: e.get_attribute("href"),
                self.browser.find_elements_by_xpath("//a"),
            ),
        )
        self.assertGreater(
            self.browser.page_source.index(self.department.open_hours), 1
        )
        self.assertIn(
            self.department.website,
            map(
                lambda e: e.get_attribute("href"),
                self.browser.find_elements_by_xpath("//a"),
            ),
        )

    def test_participation(self):
        print(self.browser.page_source)
        # Check that the page contains all participating activities
        activities = self.browser.find_elements_by_xpath(
            "//section[@id='participation']/table/tbody/tr"
        )
        self.assertEqual(8, len(activities))
        self.assertEqual(
            self.activities[self.department.name]["FORLØB"][False]["historic"][
                "participate"
            ].name,
            activities[0].find_element_by_xpath("td[@data-label='Aktivitet']").text,
        )
        self.assertEqual(
            self.activities[self.department.name]["FORLØB"][False]["active"][
                "participate"
            ].name,
            activities[1].find_element_by_xpath("td[@data-label='Aktivitet']").text,
        )
        self.assertEqual(
            self.activities[self.department.name]["FORLØB"][True]["historic"][
                "participate"
            ].name,
            activities[2].find_element_by_xpath("td[@data-label='Aktivitet']").text,
        )
        self.assertEqual(
            self.activities[self.department.name]["FORLØB"][True]["active"][
                "participate"
            ].name,
            activities[3].find_element_by_xpath("td[@data-label='Aktivitet']").text,
        )
        self.assertEqual(
            self.activities[self.department.name]["ARRANGEMENT"][False]["historic"][
                "participate"
            ].name,
            activities[4].find_element_by_xpath("td[@data-label='Aktivitet']").text,
        )
        self.assertEqual(
            self.activities[self.department.name]["ARRANGEMENT"][False]["active"][
                "participate"
            ].name,
            activities[5].find_element_by_xpath("td[@data-label='Aktivitet']").text,
        )
        self.assertEqual(
            self.activities[self.department.name]["ARRANGEMENT"][True]["historic"][
                "participate"
            ].name,
            activities[6].find_element_by_xpath("td[@data-label='Aktivitet']").text,
        )
        self.assertEqual(
            self.activities[self.department.name]["ARRANGEMENT"][True]["active"][
                "participate"
            ].name,
            activities[7].find_element_by_xpath("td[@data-label='Aktivitet']").text,
        )

    def test_open_activities(self):
        # Check that the page contains all activities
        activities = self.browser.find_elements_by_xpath(
            "//section[@id='open_activities']/table/tbody/tr"
        )
        self.assertEqual(8, len(activities))
        self.assertEqual(
            self.activities[self.department.name]["ARRANGEMENT"][True]["active"][
                "signup_due"
            ].name,
            activities[0].find_element_by_xpath("td[@data-label='Aktivitet']").text,
        )
        self.assertEqual(
            self.activities[self.department.name]["ARRANGEMENT"][False]["active"][
                "signup_due"
            ].name,
            activities[1].find_element_by_xpath("td[@data-label='Aktivitet']").text,
        )
        self.assertEqual(
            self.activities[self.department.name]["FORLØB"][True]["active"][
                "signup_due"
            ].name,
            activities[2].find_element_by_xpath("td[@data-label='Aktivitet']").text,
        )
        self.assertEqual(
            self.activities[self.department.name]["FORLØB"][False]["active"][
                "signup_due"
            ].name,
            activities[3].find_element_by_xpath("td[@data-label='Aktivitet']").text,
        )
        self.assertEqual(
            self.activities[self.department.name]["ARRANGEMENT"][True]["active"][
                "recent"
            ].name,
            activities[4].find_element_by_xpath("td[@data-label='Aktivitet']").text,
        )
        self.assertEqual(
            self.activities[self.department.name]["ARRANGEMENT"][False]["active"][
                "recent"
            ].name,
            activities[5].find_element_by_xpath("td[@data-label='Aktivitet']").text,
        )
        self.assertEqual(
            self.activities[self.department.name]["FORLØB"][True]["active"][
                "recent"
            ].name,
            activities[6].find_element_by_xpath("td[@data-label='Aktivitet']").text,
        )
        self.assertEqual(
            self.activities[self.department.name]["FORLØB"][False]["active"][
                "recent"
            ].name,
            activities[7].find_element_by_xpath("td[@data-label='Aktivitet']").text,
        )
