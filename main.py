import os
from reddit import get_hottest_posts
from image import create_custom_image
from redditScreenshot import take_screenshot_from_html
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
    return url[25:].replace("/", "_").replace("?", "_").replace(":", "_").replace("*", "_").replace("|", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("\\", "_")


numberOfPosts = 3

posts = get_hottest_posts('AskReddit', numberOfPosts)

for post in posts:
    if post:
        html_content = post['HTML_Content']
        fileName = modifyFileName(post['URL'])
        folderName = replaceSpecialCharacters(post['URL']).split('_')[0]

        screenshot_path = os.path.join("Output", folderName ,fileName ,"post_screenshot.png")
        whole_screenshot_path = os.path.join("Output", folderName, fileName ,"page_screenshot.png")

        take_screenshot_from_html(html_content, screenshot_path, 'shreddit-post')
        take_screenshot_from_html(html_content, whole_screenshot_path, 'body')
    else:
        print("Failed to fetch posts.")

#authYoutube()
#service = get_authenticated_service()
#upload_video(service, os.path.join("Output", "video.mp4"), posts[0]['Title'], posts[0]['Description'], '22', ['python', 'reddit'])