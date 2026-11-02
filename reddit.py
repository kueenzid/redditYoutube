import praw
import prawcore
import config
import requests

def is_mod_comment(comment, moderators):
    # distinguished is "moderator" or "admin" when posted with the mod badge,
    # stickied comments are almost always from AutoModerator or the mods
    author = comment.author.name.lower() if comment.author else ""
    return comment.distinguished is not None or comment.stickied or author == "automoderator" or author in moderators

def get_hottest_posts(subreddit_name, limit, comment_count):
    # Initialize the Reddit instance with your credentials
    reddit = praw.Reddit(
        client_id=config.client_id,
        client_secret=config.client_secret,
        user_agent=config.user_agent
    )

    # Access the specified subreddit
    subreddit = reddit.subreddit(subreddit_name)

    # The moderator list is not readable for every subreddit, then only badge and sticky are checked
    try:
        moderators = {moderator.name.lower() for moderator in subreddit.moderator()}
    except prawcore.exceptions.PrawcoreException:
        moderators = set()

    # Fetch the hottest posts
    hottest_posts = subreddit.top(time_filter='day', limit=limit)

    # Prepare the data
    posts_data = []
    for post in hottest_posts:
        response = requests.get(post.url)
        html_content = response.text if response.status_code == 200 else "Failed to fetch HTML content"

        post_info = {
            "Title": post.title,
            "Score": post.score,
            "Author": post.author.name if post.author else "N/A",
            "URL": post.url,
            "Comments": post.num_comments,
            "Description": post.selftext if post.selftext else 'No description available.',
            "HTML_Content": html_content,  # Add the HTML content here
            "Top_Comments": []
        }

        # Fetch the top comments for the post, without comments from moderators
        post.comments.replace_more(limit=0)
        top_comments = [c for c in post.comments.list() if not is_mod_comment(c, moderators)][:comment_count]
        for comment in top_comments:
            post_info["Top_Comments"].append({
                "Author": comment.author.name if comment.author else "N/A",
                "Body": comment.body,
                "Score": comment.score
            })

        posts_data.append(post_info)

    return posts_data
