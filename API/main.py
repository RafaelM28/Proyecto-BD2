import os
import tweepy
from dotenv import load_dotenv

# Cargar credenciales desde .env
load_dotenv()

# Autenticación
client = tweepy.Client(
    bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
    consumer_key=os.getenv("TWITTER_API_KEY"),
    consumer_secret=os.getenv("TWITTER_API_SECRET"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
)

# Obtener tweets de un usuario
def get_tweets(username: str, max_tweets: int = 10):
    try:
        user = client.get_user(username=username)
        tweets = client.get_users_tweets(
            id=user.data.id,
            max_results=max_tweets,
            tweet_fields=["created_at", "public_metrics"]
        )
        for tweet in tweets.data:
            print(f"📅 {tweet.created_at}\n📝 {tweet.text}\n---")
    except Exception as e:
        print(f"Error: {e}")

# Ejemplo de uso
if __name__ == "__main__":
    get_tweets("elonmusk", max_tweets=5)