import os
import tweepy
from dotenv import load_dotenv

# Cargar credenciales desde archivo .env
load_dotenv("credencialesTwitter.env")

# Credenciales necesarias
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

if not all([BEARER_TOKEN, API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
    print("❌ Error: Falta una o más credenciales en el archivo .env")
    exit()

# Crear cliente de la API
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

# 🔁 Función para obtener top replies a un tweet original
def get_top_replies(original_tweet_id, author_username, max_replies=5):
    query = f"conversation_id:{original_tweet_id} is:reply to:{author_username}"

    response = client.search_recent_tweets(
        query=query,
        max_results=100,
        tweet_fields=["created_at", "public_metrics", "in_reply_to_user_id"],
        expansions=["author_id"]
    )

    if not response.data:
        return []

    replies = response.data

    # Ordenar por interacciones (likes + retweets)
    sorted_replies = sorted(
        replies,
        key=lambda x: x.public_metrics["like_count"] + x.public_metrics["retweet_count"],
        reverse=True
    )

    return sorted_replies[:max_replies]

# 🔍 Función principal para buscar tweets originales y respuestas
def search_tweets(keyword: str, max_tweets: int = 5):
    try:
        print(f"🔎 Buscando tweets originales con: '{keyword}'\n")

        query = f"{keyword} -is:reply -is:retweet"

        response = client.search_recent_tweets(
            query=query,
            max_results=max_tweets,
            tweet_fields=["created_at", "public_metrics", "author_id", "conversation_id"],
            expansions=["author_id"]
        )

        if not response.data:
            print("⚠️ No se encontraron tweets originales.")
            return

        for tweet in response.data:
            author = client.get_user(id=tweet.author_id)
            username = author.data.username

            print(f"🧵 TWEET ORIGINAL ({username})")
            print(f"📅 {tweet.created_at}")
            print(f"📝 {tweet.text}")
            print(f"❤️ {tweet.public_metrics['like_count']} | 🔁 {tweet.public_metrics['retweet_count']}\n")

            replies = get_top_replies(tweet.id, username)

            if replies:
                for idx, reply in enumerate(replies, 1):
                    print(f"   ↪️ RESPUESTA #{idx}")
                    print(f"   📝 {reply.text}")
                    print(f"   ❤️ {reply.public_metrics['like_count']} | 🔁 {reply.public_metrics['retweet_count']}\n")
            else:
                print("   😶 Sin respuestas destacadas encontradas.\n")

    except tweepy.TweepyException as e:
        print(f"❌ Error en la API de Twitter: {e}")

# 🚀 Punto de entrada
if __name__ == "__main__":
    search_tweets("guerra de aranceles, trump", max_tweets=5)
