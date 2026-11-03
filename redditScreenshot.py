import os
import base64
import random
import asyncio
from playwright.async_api import async_playwright
import config

# Removes the cookie banner without accepting it and hides the sticky header and bottom bar
HIDE_20MIN_OVERLAYS = """() => {
    document.getElementById('onetrust-consent-sdk')?.remove();
    document.documentElement.style.overflow = 'auto';
    document.body.style.overflow = 'auto';
    for (const element of document.querySelectorAll('body *')) {
        const position = getComputedStyle(element).position;
        if (position === 'fixed' || position === 'sticky') element.style.visibility = 'hidden';
    }
}"""

# Default profile picture of 20min, used for every comment instead of the real one
# Copy of https://api.20min.ch/user/static/15@4x.1a9d6907bd8a7b66b15d3dc47dd8533469c08e25431f80e0a865d29ce4753ebc.png
DEFAULT_20MIN_AVATAR_FILE = os.path.join("assets", "20min", "default_avatar.png")


def default_20min_avatar():
    """Returns the default profile picture as data URI, so the page does not load it from 20min."""
    with open(DEFAULT_20MIN_AVATAR_FILE, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

# Hides the comment text, time and menu button, censors the nickname and shows the default profile picture,
# so only nickname and the reaction bar of 20min are left
PREPARE_20MIN_COMMENT = """(comment, args) => {
    const normalize = text => text.replace(/\\s+/g, ' ').trim();
    // The outermost element that starts with the comment text but does not contain the reaction bar
    const body = [...comment.querySelectorAll('*')].find(
        e => normalize(e.innerText || '').startsWith(args.prefix) && !/Lesende/.test(e.innerText)
    );
    if (body) body.style.display = 'none';

    const nickname = [...comment.querySelectorAll('*')].find(
        e => e.children.length === 0 && e.textContent.trim() === args.nickname
    );
    if (nickname) nickname.textContent = args.censored;

    comment.querySelectorAll('picture source').forEach(source => source.remove());
    comment.querySelectorAll('img').forEach(image => {
        image.removeAttribute('srcset');
        image.src = args.avatar;
    });

    const top = comment.getBoundingClientRect().top;
    [...comment.querySelectorAll('*')].filter(e =>
        e.children.length === 0 && e.getBoundingClientRect().top - top < 80 &&
        /^(vor |gerade|gestern|\\d{1,2}\\.\\d{1,2}\\.)/i.test(e.textContent.trim())
    ).forEach(time => time.style.display = 'none');
    comment.querySelectorAll('button').forEach(button => {
        if (!button.innerText.trim() && button.getBoundingClientRect().top - top < 80) button.style.visibility = 'hidden';
    });
    comment.style.padding = '16px';

    // Replies are nested in the comment below its reaction bar: hide the whole reply thread,
    // and the screenshot also ends after the bar
    const label = [...comment.querySelectorAll('*')].find(e => e.children.length === 0 && /Lesende/.test(e.textContent));
    comment.querySelectorAll('article').forEach(reply => {
        let thread = reply;
        while (thread.parentElement && thread.parentElement !== comment && !thread.parentElement.contains(label)) thread = thread.parentElement;
        thread.style.display = 'none';
    });
    return {body: !!body, nickname: !!nickname, bottom: label ? label.getBoundingClientRect().bottom : null};
}"""

# The bookmark button is the last button of a teaser; padding keeps the text off the image edge
PREPARE_20MIN_TEASER = """teaser => {
    const buttons = teaser.querySelectorAll('button');
    if (buttons.length) buttons[buttons.length - 1].style.visibility = 'hidden';
    teaser.style.padding = '16px';
}"""


class ScreenshotTaker:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None

    async def start(self, source="reddit"):
        self.playwright = await async_playwright().start()

        if source == "20min":
            # Mobile layout: every teaser is full width, scale 3 keeps small teasers sharp in the video
            self.browser = await self.playwright.chromium.launch()
            self.context = await self.browser.new_context(
                locale="de-CH",
                color_scheme="dark",
                viewport={"width": 412, "height": 915},
                device_scale_factor=3,
            )
            self.page = await self.context.new_page()
            self.page.set_default_timeout(60000)
            return

        self.browser = await self.playwright.chromium.launch(headless=True)
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
        await self.page.fill("#login-username input[name='username']", config.username)

        await self.random_pause()
        await self.page.keyboard.press("Tab")

        await self.page.wait_for_selector("#login-password")
        await self.random_pause()
        await self.page.fill("#login-password input[name='password']", config.password)

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

    async def take_20min_screenshot(self, article_id, output_path, urls):
        """Screenshots the teaser of the article on the first page that has it, returns False if none has it."""
        for url in urls:
            await self.page.goto(url, wait_until="domcontentloaded")
            await self.page.wait_for_timeout(4000)
            await self.page.evaluate(HIDE_20MIN_OVERLAYS)

            teaser = self.page.locator("article").filter(has=self.page.locator(f'a[href$="-{article_id}"]')).first
            if await teaser.count() == 0:
                continue

            await teaser.scroll_into_view_if_needed()
            await self.page.wait_for_timeout(1500)  # lazy loaded images
            await self.page.evaluate(HIDE_20MIN_OVERLAYS)
            await teaser.evaluate(PREPARE_20MIN_TEASER)
            await teaser.screenshot(path=output_path)
            return True
        return False

    async def take_20min_comment_screenshots(self, url, comments, output_paths):
        """Screenshots each comment on the 20min comment page without its text, returns True for every comment found."""
        await self.page.goto(url, wait_until="domcontentloaded")
        await self.page.wait_for_timeout(4000)
        await self.page.evaluate(HIDE_20MIN_OVERLAYS)

        avatar = default_20min_avatar()
        found = []
        for comment, output_path in zip(comments, output_paths):
            prefix = " ".join(comment["Body"].split())[:50]
            element = self.page.locator("article").filter(has_text=prefix).first

            # The page loads more comments while scrolling
            for _ in range(30):
                if await element.count():
                    break
                await self.page.mouse.wheel(0, 4000)
                await self.page.wait_for_timeout(600)
            if not await element.count():
                found.append(False)
                continue

            # Comments with many replies can be taller than the screen, so align the top
            await element.evaluate("element => element.scrollIntoView({block: 'start'})")
            await self.page.wait_for_timeout(1000)
            await self.page.evaluate(HIDE_20MIN_OVERLAYS)
            result = await element.evaluate(PREPARE_20MIN_COMMENT, {
                "prefix": prefix, "nickname": comment["Nickname"], "censored": comment["Author"], "avatar": avatar
            })
            # Never screenshot an uncensored nickname, the comment text or the replies
            if not (result["body"] and result["nickname"] and result["bottom"]):
                found.append(False)
                continue
            await self.page.wait_for_timeout(800)  # default profile picture
            box = await element.bounding_box()
            await self.page.screenshot(path=output_path, clip={
                "x": box["x"], "y": box["y"], "width": box["width"], "height": result["bottom"] + 16 - box["y"]
            })
            found.append(True)
        return found

    async def close(self):
        await self.browser.close()
        await self.playwright.stop()
