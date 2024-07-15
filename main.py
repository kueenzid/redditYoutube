import os
from reddit import get_hottest_posts
from image import create_custom_image
from redditScreenshot import take_screenshot_from_html
from Youtube.auth import authenticate as authYoutube
from Youtube.upload import upload_video, get_authenticated_service

posts = get_hottest_posts('python', 1)

if posts:
    html_content = posts[0]['HTML_Content']
    screenshot_path = os.path.join("Output", "post_screenshot.png")
    whole_screenshot_path = os.path.join("Output", "page_screenshot.png")

    take_screenshot_from_html(html_content, screenshot_path, 'shreddit-post')
    take_screenshot_from_html(html_content, whole_screenshot_path, 'body')
else:
    print("Failed to fetch posts.")

#authYoutube()
#service = get_authenticated_service()
#upload_video(service, os.path.join("Output", "video.mp4"), posts[0]['Title'], posts[0]['Description'], '22', ['python', 'reddit'])