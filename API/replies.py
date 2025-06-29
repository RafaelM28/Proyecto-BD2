import os
import tweepy
from dotenv import load_dotenv

load_dotenv()
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
client = tweepy.Client(bearer_token=BEARER_TOKEN)

def get_top_replies(tweet_id, username, max_replies=3):
    query = f"conversation_id:{tweet_id} is:reply to:{username}"
    try:
        response = client.search_recent_tweets(
            query=query,
            max_results=50,
            tweet_fields=["created_at", "public_metrics"],
            expansions=["author_id"]
        )
        if not response.data:
            return []

        replies = sorted(response.data, key=lambda x: x.public_metrics['like_count'] + x.public_metrics['retweet_count'], reverse=True)
        return [{
            "text": r.text,
            "likes": r.public_metrics['like_count'],
            "retweets": r.public_metrics['retweet_count']
        } for r in replies[:max_replies]]

    except Exception as e:
        return []

def get_tweets_with_top_replies(username: str, max_tweets: int = 5):
    try:
        user = client.get_user(username=username)
        if user.data is None:
            return []

        user_id = user.data.id
        tweets = client.get_users_tweets(id=user_id, max_results=max_tweets, tweet_fields=["created_at", "public_metrics", "conversation_id"])

        result = []
        for tweet in tweets.data:
            replies = get_top_replies(tweet.id, username)
            result.append({
                "text": tweet.text,
                "likes": tweet.public_metrics['like_count'],
                "retweets": tweet.public_metrics['retweet_count'],
                "replies": replies
            })

        return result

    except Exception:
        return []
