import os
import tempfile
from playwright.sync_api import sync_playwright



import config


def take_screenshot(url, output_path, css_selector):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
        )
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        page = context.new_page()

        page.goto('https://www.reddit.com/login/', wait_until='load')
        page.screenshot(path=output_path)

        page.wait_for_selector('#login-username')

        page.fill('#login-username', config.username)
        page.fill('#login-password', config.password)
        page.click('button[type="submit"]')

        page.wait_for_navigation()


        page.goto(url)
        page.wait_for_selector(css_selector)

        element = page.query_selector(css_selector)
        element.screenshot(path=output_path)

        browser.close()