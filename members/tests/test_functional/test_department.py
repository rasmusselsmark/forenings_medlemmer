import os
import socket
from datetime import timedelta

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
                for variant in ["participate", "recent", "old"]:
                    self.activities[dep.name][activity_type][
                        variant
                    ] = ActivityFactory.create(
                        open_invite=True,
                        min_age=5,
                        max_age=90,
                        department=dep,
                        signup_closing=(
                            Faker("past_date", start_date="-10d")
                            if variant == "old"
                            else Faker("future_datetime", end_date="+100d")
                        ),
                        name=f"{dep.name}-{activity_type}-{variant}",
                        activitytype_id=activity_type,
                    )
                    if variant == "participate":
                        ActivityParticipantFactory.create(
                            activity=self.activities[dep.name][activity_type][variant],
                            member=self.member,
                        )

        self.browser = webdriver.Remote(
            "http://selenium:4444/wd/hub", DesiredCapabilities.CHROME
        )

    def tearDown(self):
        if not os.path.exists("test-screens"):
            os.mkdir("test-screens")
        self.browser.save_screenshot("test-screens/department_list_final.png")
        self.browser.quit()

    def test_department(self):
        log_in(self, self.member.person)
        # Loads the department resource
        self.browser.get(f"{self.live_server_url}/departments/{self.department.name}")
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

        # Check that the page contains all participating activities
        activity_names = [
            e.text
            for e in self.browser.find_elements_by_xpath(
                "//section[@id='participation']/table/tbody/tr/td[@data-label='Aktivitet']"
            )
        ]
        self.assertEqual(2, len(activity_names))
        self.assertIn(
            self.activities[self.department.name]["ARRANGEMENT"]["participate"].name,
            activity_names,
        )
        self.assertIn(
            self.activities[self.department.name]["FORLØB"]["participate"].name,
            activity_names,
        )

        # Check that the page contains all activities
        activity_names = [
            e.text
            for e in self.browser.find_elements_by_xpath(
                "//section[@id='open_activities']/table/tbody/tr/td[@data-label='Aktivitet']"
            )
        ]
        self.assertEqual(2, len(activity_names))
        self.assertIn(
            self.activities[self.department.name]["ARRANGEMENT"]["recent"].name,
            activity_names,
        )
        self.assertIn(
            self.activities[self.department.name]["FORLØB"]["recent"].name,
            activity_names,
        )
