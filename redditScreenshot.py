import random
import asyncio
from playwright.async_api import async_playwright
import config


class ScreenshotTaker:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.context = await self.browser.new_context(
            locale="en-us",
            color_scheme="dark",
            user_agent=self.random_user_agent(),
            viewport={"width": 720, "height": 720},
        )
        self.page = await self.context.new_page()
        self.page.set_default_timeout(60000)
        await self.change_zoom_factor(self.page, 2)
        await self._login()

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
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
        ]
        return random.choice(user_agents)

    async def _login(self):
        await self.page.goto("https://www.reddit.com/login/", wait_until="load")

        await self.page.wait_for_selector("#login-username")
        await self.random_pause()
        await self.page.fill("#login-username", config.username)

        await self.random_pause()
        await self.page.keyboard.press("Tab")

        await self.page.wait_for_selector("#login-password")
        await self.random_pause()
        await self.page.fill("#login-password", config.password)

        await self.random_pause()

        async with self.page.expect_navigation(timeout=60000):
            await self.page.keyboard.press("Enter")

    async def change_zoom_factor(self, page, zoom_factor=2):
        await page.evaluate(f"""
        document.body.style.transform = "scale({zoom_factor})";
        document.body.style.transformOrigin = "0 0";
        document.body.style.width = "{100 / zoom_factor}%";
        document.body.style.height = "{100 / zoom_factor}%";
    """)

    async def random_pause(self):
        random_pause = random.uniform(0.5, 2)
        await asyncio.sleep(random_pause)

    async def take_screenshot(self, url, output_path, css_selector):
        await self.page.goto(url, wait_until="load")
        await self.change_zoom_factor(self.page, 2)
        await self.page.wait_for_timeout(5000)
        await self.page.wait_for_selector(css_selector)

        element = await self.page.query_selector(css_selector)
        await element.screenshot(path=output_path)

    async def close(self):
        await self.browser.close()
        await self.playwright.stop()
