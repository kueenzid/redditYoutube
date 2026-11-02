import asyncio
import os
import re
from reddit import get_hottest_posts
from twenty_min import get_top_articles
from image import create_custom_image, create_title_card, create_comment_card
from redditScreenshot import ScreenshotTaker
from TextToSpeech_Local import TextToSpeech_Local
from TextToSpeech_External import TextToSpeech_External
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
    return re.sub(r"\W", "_", url[25:])


async def main():
    source = "20min"  # "reddit" or "20min"
    subreddit_name = "ask"
    numberOfPosts = 1
    comment_count = 2

    output_folder = "Output"
    language = "de" if source == "20min" else "en"
    tts_engine = "edge"  # "edge" (external), "xtts", "coqui" or "bark"
    is_screenshot_taker = source == "reddit"
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
        if tts_engine == "edge":
            # Voices are set in TextToSpeech_External.edge_voices
            titleTextToSpeech = TextToSpeech_External(tts_engine, language, "title")
            textToSpeech = TextToSpeech_External(tts_engine, language, "comment")
        else:
            textToSpeech = TextToSpeech_Local(tts_engine, language)
            titleTextToSpeech = textToSpeech

    if source == "20min":
        posts = get_top_articles(numberOfPosts, comment_count)
    else:
        posts = get_hottest_posts(subreddit_name, numberOfPosts, comment_count)

    for post in posts:
        if post:
            url = post["URL"]
            if source == "20min":
                pathName = os.path.join(output_folder, "20min", post["Id"])
            else:
                fileName = modifyFileName(post["URL"])
                folderName = replaceSpecialCharacters(post["URL"]).split("_")[0]
                pathName = os.path.join(output_folder, folderName, fileName)
            os.makedirs(pathName, exist_ok=True)

            screenshot_path = os.path.join(pathName, "post_screenshot.png")
            if is_screenshot_taker:
                await screenshot_taker.take_screenshot(
                    url, screenshot_path, "shreddit-post"
                )
            elif source == "20min":
                create_title_card(
                    screenshot_path, post["Title"], "20 Minuten", f"{post['Comments']} Kommentare"
                )
                for i, comment in enumerate(post["Top_Comments"]):
                    create_comment_card(
                        os.path.join(pathName, f"comment_card_{i}.png"), comment["Author"], comment["Reactions"]
                    )

            if is_textToSpeech:
                titleTextToSpeech.create_text_to_speech_file(
                    post["Title"], os.path.join(pathName, "title.wav")
                )

                for i, comment in enumerate(post["Top_Comments"]):
                    textToSpeech.create_text_to_speech_file(
                        comment["Body"], os.path.join(pathName, f"comment_{i}.wav")
                    )

            generate_video(pathName, comment_count, language)

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
