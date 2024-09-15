import asyncio
import os
import re
from reddit import get_hottest_posts
from image import create_custom_image
from redditScreenshot import ScreenshotTaker
from TextToSpeech_Local import TextToSpeech_Local
from VideoGenerator import generate_video


def modifyFileName(url):
    modified_fileName = replaceSpecialCharacters(url)

    first_underscore_index = modified_fileName.find("_")

    if first_underscore_index == -1:
        return modified_fileName

    second_underscore_index = modified_fileName.find("_", first_underscore_index + 1)

    if second_underscore_index == -1:
        return modified_fileName

    return modified_fileName[second_underscore_index + 1 :]


def replaceSpecialCharacters(url):
    return re.sub("\W", "_", url[25:])


async def main():
    subreddit_name = "ask"
    numberOfPosts = 1
    comment_count = 2

    output_folder = "Output"
    is_screenshot_taker = True
    is_textToSpeech = True

    if is_screenshot_taker:
        screenshot_taker = ScreenshotTaker()
        while True:
            try:
                await screenshot_taker.start()
                break
            except Exception as e:
                print(e)
                print("Error occurred while starting the screenshot taker. Retrying...")

    if is_textToSpeech:
        textToSpeech = TextToSpeech_Local()

    posts = get_hottest_posts(subreddit_name, numberOfPosts, comment_count)

    for post in posts:
        if post:
            url = post["URL"]
            fileName = modifyFileName(post["URL"])
            folderName = replaceSpecialCharacters(post["URL"]).split("_")[0]
            pathName = os.path.join(output_folder, folderName, fileName)

            if is_screenshot_taker:
                screenshot_path = os.path.join(pathName, "post_screenshot.png")
                await screenshot_taker.take_screenshot(
                    url, screenshot_path, "shreddit-post"
                )

            if is_textToSpeech:
                textToSpeech.create_text_to_speech_file(
                    post["Title"], os.path.join(pathName, "title.wav")
                )

                for i, comment in enumerate(post["Top_Comments"]):
                    textToSpeech.create_text_to_speech_file(
                        comment["Body"], os.path.join(pathName, f"comment_{i}.wav")
                    )

            generate_video(pathName)

            # Create .txt file with post information
            txt_file_path = os.path.join(pathName, "comments.txt")
            with open(txt_file_path, "w", encoding="utf-8") as txt_file:
                for i, comment in enumerate(post["Top_Comments"]):
                    txt_file.write(f"{comment['Body']}\n\n")

        else:
            print("Failed to fetch posts.")

    if is_screenshot_taker:
        await screenshot_taker.close()

    # authYoutube()
    # service = get_authenticated_service()
    # upload_video(service, os.path.join("Output", "video.mp4"), posts[0]['Title'], posts[0]['Description'], '22', ['python', 'reddit'])


if __name__ == "__main__":
    asyncio.run(main())
