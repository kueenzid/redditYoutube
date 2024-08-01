import os
import tempfile
from playwright.sync_api import sync_playwright
import config

class ScreenshotTaker:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context(
            locale="en-us",
            color_scheme="dark",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        self.page = self.context.new_page()
        self._login()

    def _login(self):
        self.page.goto('https://www.reddit.com/login/', wait_until='load')
        #self.page.screenshot(path="login_page.png")

        self.page.wait_for_selector('#login-username')
        self.page.fill('#login-username', config.username)

        self.page.wait_for_selector('#login-password')
        self.page.fill('#login-password', config.password)

        with self.page.expect_navigation():
            self.page.click('button[type="button"]')

    def take_screenshot(self, url, output_path, css_selector):
        self.page.goto(url)

        self.page.wait_for_selector(css_selector)

        element = self.page.query_selector(css_selector)
        element.screenshot(path=output_path)

    def close(self):
        self.browser.close()
        self.playwright.stop()
