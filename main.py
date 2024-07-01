from reddit import get_hottest_posts
from image import create_custom_image

posts = get_hottest_posts('python', 1)

create_custom_image('output.png', posts[0]['Title'])