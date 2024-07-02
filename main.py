import os
from reddit import get_hottest_posts
from image import create_custom_image
from Youtube.auth import authenticate as authYoutube
from Youtube.upload import upload_video, get_authenticated_service

posts = get_hottest_posts('python', 1)

create_custom_image(os.path.join("Output", "output.png"), posts[0]['Title'])

authYoutube()
service = get_authenticated_service()
upload_video(service, os.path.join("Output", "video.mp4"), posts[0]['Title'], posts[0]['Description'], '22', ['python', 'reddit'])