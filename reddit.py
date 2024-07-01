import praw
import config

def get_hottest_posts(subreddit_name, limit=1):
    # Initialize the Reddit instance with your credentials
    reddit = praw.Reddit(
        client_id=config.client_id,
        client_secret=config.client_secret,
        user_agent=config.user_agent
    )

    # Access the specified subreddit
    subreddit = reddit.subreddit(subreddit_name)

    # Fetch the hottest posts
    hottest_posts = subreddit.hot(limit=limit)

    # Prepare the data
    posts_data = []
    for post in hottest_posts:
        post_info = {
            "Title": post.title,
            "Score": post.score,
            "Author": post.author.name if post.author else "N/A",
            "URL": post.url,
            "Comments": post.num_comments,
            "Description": post.selftext if post.selftext else 'No description available.',
            "Top_Comments": []
        }

        # Fetch the top 5 comments for the post
        post.comments.replace_more(limit=0)
        top_comments = post.comments.list()[:5]
        for comment in top_comments:
            post_info["Top_Comments"].append({
                "Author": comment.author.name if comment.author else "N/A",
                "Body": comment.body,
                "Score": comment.score
            })

        posts_data.append(post_info)

    return posts_data
