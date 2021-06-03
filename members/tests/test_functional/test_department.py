import socket
import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from members.tests.factories import DepartmentFactory
from django.utils import timezone
from datetime import timedelta

"""
This test goes to a department page

"""


class DepartmentTest(StaticLiveServerTestCase):
    host = socket.gethostbyname(socket.gethostname())
    serialized_rollback = True

    def setUp(self):
        self.department_1 = DepartmentFactory.create(
            created=(timezone.now() - timedelta(days=5)).date(),
            isVisible=True,
            closed_dtm=None,
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
        # Loads the department resource
        self.browser.get(f"{self.live_server_url}/departments/{self.department_1.name}")
        self.assertIn(
            self.department_1.name,
            map(lambda e: e.text, self.browser.find_elements_by_xpath("//*")),
        )
