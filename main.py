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


subreddit_name = 'AskReddit'
numberOfPosts = 1
comment_count = 0


output_folder = 'Output'

# for debugging purposes. normally set to True
is_screenshot_taker = False
is_textToSpeech = True
is_videoGenerator = False

# available TTS engines
COQUI_TTS = 'coqui'
BARK_TTS = 'bark'

if is_screenshot_taker:
    screenshot_taker = ScreenshotTaker()
if is_textToSpeech:
    tts = TextToSpeech_Local(engine=BARK_TTS)

posts = get_hottest_posts(subreddit_name, numberOfPosts, comment_count)

for post in posts:
    if post:
        url = post['URL']
        fileName = modifyFileName(post['URL'])
        folderName = replaceSpecialCharacters(post['URL']).split('_')[0]
        pathName = os.path.join(output_folder, folderName, fileName)

        if is_screenshot_taker:
            screenshot_path = os.path.join(pathName, "post_screenshot.png")
            screenshot_taker.take_screenshot(url, screenshot_path, 'shreddit-post')
            screenshot_taker.close()

        if is_textToSpeech:
            tts.create_text_to_speech_file(post['Title'], os.path.join(pathName, "title.wav"))

            for i, comment in enumerate(post['Top_Comments']):
                tts.create_text_to_speech_file(comment['Body'], os.path.join(pathName, f"comment_{i}.wav"))

        if is_videoGenerator:
            generate_video(pathName, comment_count)

        # Create .txt file with post information
        txt_file_path = os.path.join(pathName, "comments.txt")
        with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(f"Title: {post['Title']}\n\n")
            txt_file.write(f"URL: {post['URL']}\n\n")

            for i, comment in enumerate(post['Top_Comments']):
                txt_file.write(f"{comment['Body']}\n\n")

    else:
        print("Failed to fetch posts.")

# authYoutube()
# service = get_authenticated_service()
# upload_video(service, os.path.join("Output", "video.mp4"), posts[0]['Title'], posts[0]['Description'], '22', ['python', 'reddit'])