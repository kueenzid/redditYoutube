import asyncio
import os
import re
from reddit import get_hottest_posts
from image import create_custom_image
from redditScreenshot import ScreenshotTaker
from Youtube.auth import authenticate as authYoutube
from Youtube.upload import upload_video, get_authenticated_service

def modifyFileName(url):
    modified_fileName = replaceSpecialCharacters(url)

    first_underscore_index = modified_fileName.find('_')

    if first_underscore_index == -1:
        return modified_fileName

    second_underscore_index = modified_fileName.find('_', first_underscore_index + 1)

    if second_underscore_index == -1:
        return modified_fileName

    return modified_fileName[second_underscore_index + 1:]


def replaceSpecialCharacters(url):
    return re.sub("\W", "_", url[25:])


numberOfPosts = 3

posts = get_hottest_posts('AskReddit', numberOfPosts)

screenshot_taker = ScreenshotTaker()


for post in posts:
    if post:
        url = post['URL']
        fileName = modifyFileName(post['URL'])
        folderName = replaceSpecialCharacters(post['URL']).split('_')[0]

        screenshot_path = os.path.join("Output", folderName ,fileName ,"post_screenshot.png")
        screenshot_taker.take_screenshot(url, screenshot_path, 'shreddit-post')

        #whole_screenshot_path = os.path.join("Output", folderName, fileName ,"page_screenshot.png")
        #take_screenshot(url, whole_screenshot_path, 'body')
    else:
        print("Failed to fetch posts.")

screenshot_taker.close()

#authYoutube()
#service = get_authenticated_service()
#upload_video(service, os.path.join("Output", "video.mp4"), posts[0]['Title'], posts[0]['Description'], '22', ['python', 'reddit'])