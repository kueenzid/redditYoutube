import asyncio
import os
import re
from reddit import get_hottest_posts
from image import create_custom_image
from redditScreenshot import ScreenshotTaker
from TextToSpeech_Local import TextToSpeech_Local
from VideoGenerator import generate_video
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


numberOfPosts = 1
output_folder = "Output"

screenshot_taker = ScreenshotTaker()
textToSpeech = TextToSpeech_Local()

posts = get_hottest_posts('AskReddit', numberOfPosts)



for post in posts:
    if post:
        url = post['URL']
        fileName = modifyFileName(post['URL'])
        folderName = replaceSpecialCharacters(post['URL']).split('_')[0]
        pathName = os.path.join(output_folder, folderName, fileName)

        screenshot_path = os.path.join(pathName, "post_screenshot.png")
        screenshot_taker.take_screenshot(url, screenshot_path, 'shreddit-post')

        #whole_screenshot_path = os.path.join("Output", folderName, fileName ,"page_screenshot.png")
        #take_screenshot(url, whole_screenshot_path, 'body')

        textToSpeech.create_text_to_speech_file(post['Title'], os.path.join(pathName, "title.wav"))

        for i, comment in enumerate(post['Top_Comments']):
            textToSpeech.create_text_to_speech_file(comment['Body'], os.path.join(pathName, f"comment_{i}.wav"))

        generate_video(pathName)
    else:
        print("Failed to fetch posts.")

screenshot_taker.close()

#authYoutube()
#service = get_authenticated_service()
#upload_video(service, os.path.join("Output", "video.mp4"), posts[0]['Title'], posts[0]['Description'], '22', ['python', 'reddit'])