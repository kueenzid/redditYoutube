import os
import tempfile
from playwright.sync_api import sync_playwright

def take_screenshot_from_html(html_content, output_path, css_selector):
    # Create a temporary file to save the HTML content
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
        tmp_file_name = tmp_file.name
        tmp_file.write(html_content.encode('utf-8'))
        tmp_file.flush()

        # Use Playwright to open the temporary HTML file and take a screenshot
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f'file://{tmp_file_name}')
            # Find the element using the provided CSS selector and take a screenshot of it
            element = page.query_selector(css_selector)
            if element:
                element.screenshot(path=output_path)
            else:
                print(f"No element found for the CSS selector: {css_selector}")
            browser.close()

    # Optionally, delete the temporary file
    os.remove(tmp_file_name)