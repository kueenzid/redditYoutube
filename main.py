import asyncio
import json
import os
import re
import shutil
from reddit import get_hottest_posts
from twenty_min import get_top_articles, BASE_URL, WICHTIGSTE_ARTIKEL_URL
from image import create_custom_image, create_title_card
from redditScreenshot import ScreenshotTaker
from TextToSpeech_Local import TextToSpeech_Local
from TextToSpeech_External import TextToSpeech_External
from VideoGenerator import generate_video
from textCleanup import removeEmojis
from Youtube.upload import get_authenticated_service, upload_video


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
    comment_count = 3

    output_folder = "Output"
    language = "de" if source == "20min" else "en"
    tts_engine = "edge"  # "edge" (external), "xtts", "coqui" or "bark"
    is_screenshot_taker = True
    is_textToSpeech = True

    upload_youtube = True  # log in once with: python Youtube/auth.py
    youtube_privacy = "private"  # "private", "unlisted" or "public"
    youtube_category = "23"  # Comedy

    # Articles already uploaded, so that runs several times a day don't make the same video again
    uploaded_file = os.path.join(output_folder, "uploaded.json")
    delete_after_upload = True  # delete the folder of a video after its upload
    uploaded = []
    if os.path.exists(uploaded_file):
        with open(uploaded_file, encoding="utf-8") as f:
            uploaded = json.load(f)

    # Check the YouTube login before spending time on the videos
    if upload_youtube:
        youtube = get_authenticated_service()

    if is_screenshot_taker:
        screenshot_taker = ScreenshotTaker()
        while True:
            try:
                await screenshot_taker.start(source)
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
        posts = get_top_articles(numberOfPosts, comment_count, exclude_ids=set(uploaded))
    else:
        posts = get_hottest_posts(subreddit_name, numberOfPosts, comment_count)
        posts = [post for post in posts if post["URL"] not in uploaded]

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
            if source == "reddit":
                if is_screenshot_taker:
                    await screenshot_taker.take_screenshot(
                        url, screenshot_path, "shreddit-post"
                    )
            else:
                # Older articles are no longer on the homepage, but still on the news page
                if not (is_screenshot_taker and await screenshot_taker.take_20min_screenshot(
                    post["Id"], screenshot_path, [BASE_URL + "/", WICHTIGSTE_ARTIKEL_URL]
                )):
                    create_title_card(
                        screenshot_path, post["Title"], "20 Minuten", f"{post['Comments']} Kommentare"
                    )
                # Screenshot of the real comment on 20min (comment page sorted by reactions)
                card_paths = [os.path.join(pathName, f"comment_card_{i}.png") for i in range(len(post["Top_Comments"]))]
                found = [False] * len(card_paths)
                if is_screenshot_taker:
                    found = await screenshot_taker.take_20min_comment_screenshots(
                        f"{BASE_URL}/comment/{post['Id']}/reactions", post["Top_Comments"], card_paths
                    )
                missing = [i for i, ok in enumerate(found) if not ok]
                if missing:
                    if is_screenshot_taker:
                        await screenshot_taker.close()
                    raise RuntimeError(f"No screenshot possible for comment(s) {missing} of {url}, aborting")

            if is_textToSpeech:
                titleTextToSpeech.create_text_to_speech_file(
                    removeEmojis(post["Title"]), os.path.join(pathName, "title.wav")
                )

                for i, comment in enumerate(post["Top_Comments"]):
                    textToSpeech.create_text_to_speech_file(
                        removeEmojis(comment["Body"]), os.path.join(pathName, f"comment_{i}.wav")
                    )

            generate_video(pathName, comment_count, language)

            # Create .txt file with post information
            txt_file_path = os.path.join(pathName, "comments.txt")
            with open(txt_file_path, "w", encoding="utf-8") as txt_file:
                for i, comment in enumerate(post["Top_Comments"]):
                    txt_file.write(f"{comment['Body']}\n\n")

            if upload_youtube:
                upload_video(
                    youtube,
                    os.path.join(pathName, "output.mp4"),
                    post["Title"],
                    f"{post['Title']}\n\n{url}\n\n#shorts",
                    youtube_category,
                    ["20 Minuten", "Kommentare"] if source == "20min" else ["reddit", "comments"],
                    youtube_privacy,
                )

                uploaded.append(post.get("Id", url))
                with open(uploaded_file, "w", encoding="utf-8") as f:
                    json.dump(uploaded, f, indent=1)

                if delete_after_upload:
                    shutil.rmtree(pathName)

        else:
            print("Failed to fetch posts.")

    if is_screenshot_taker:
        await screenshot_taker.close()


if __name__ == "__main__":
    asyncio.run(main())
