import os
import tempfile
import random
import time
from playwright.sync_api import sync_playwright
import config

class ScreenshotTaker:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context(
            locale="en-us",
            color_scheme="dark",
            #user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            user_agent=self.random_user_agent(),
            viewport={"width": 720, "height": 720}
        )
        self.page = self.context.new_page()
        self.page.set_default_timeout(60000)
        self.change_zoom_factor(self.page, 2)
        self._login()

    def random_user_agent(self):
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36"
        ]
        return random.choice(user_agents)

    def _login(self):
        self.page.goto('https://www.reddit.com/login/', wait_until='load')

        self.page.wait_for_selector('#login-username')
        self.random_pause()
        self.page.fill('#login-username', config.username)

        self.random_pause()
        self.page.keyboard.press('Tab')

        self.page.wait_for_selector('#login-password')
        self.random_pause()
        self.page.fill('#login-password', config.password)

        self.random_pause()

        with self.page.expect_navigation(timeout=60000):
            #self.page.click('button[type="button"]')
            self.page.keyboard.press('Enter')

    def change_zoom_factor(self, page, zoom_factor = 2):
        page.evaluate(f'''
        document.body.style.transform = "scale({zoom_factor})";
        document.body.style.transformOrigin = "0 0";
        document.body.style.width = "{100 / zoom_factor}%";
        document.body.style.height = "{100 / zoom_factor}%";
    ''')

    def random_pause(self):
        random_pause = random.uniform(0.5, 2)
        time.sleep(random_pause)

    def take_screenshot(self, url, output_path, css_selector):
        self.page.goto(url, wait_until='load')
        self.change_zoom_factor(self.page, 2)
        self.page.wait_for_timeout(5000)
        self.page.wait_for_selector(css_selector)

        element = self.page.query_selector(css_selector)
        element.screenshot(path=output_path)

    def close(self):
        self.browser.close()
        self.playwright.stop()
