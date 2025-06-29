import os
import tweepy
from dotenv import load_dotenv

# 🌿 Cargar credenciales desde archivo .env
load_dotenv()
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# 🛡️ Validación
if not BEARER_TOKEN:
    print("❌ Error: Falta el bearer token en tu archivo .env")
    exit()

# 🌐 Cliente Tweepy
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# 🧪 Ver credencial
def debug_credentials():
    print(f"Token length: {len(BEARER_TOKEN)} chars")
    print(f"Token starts with: {BEARER_TOKEN[:10]}...")
    print(f"Token ends with: ...{BEARER_TOKEN[-10:]}")
    print(f"Full token (hidden): {BEARER_TOKEN[:5]}...{BEARER_TOKEN[-5:]}")

# 🔁 Obtener respuestas con más interacciones
def get_top_replies(tweet_id, username, max_replies=5):
    query = f"conversation_id:{tweet_id} is:reply to:{username}"
    try:
        response = client.search_recent_tweets(
            query=query,
            max_results=100,
            tweet_fields=["created_at", "public_metrics"],
            expansions=["author_id"]
        )
        if not response.data:
            return []

        replies = response.data
        replies_sorted = sorted(
            replies,
            key=lambda x: x.public_metrics['like_count'] + x.public_metrics['retweet_count'],
            reverse=True
        )
        return replies_sorted[:max_replies]

    except Exception as e:
        print(f"⚠️ Error buscando respuestas: {e}")
        return []

# 🔍 Obtener tweets + respuestas destacadas
def get_tweets(username: str, max_tweets: int = 5):
    try:
        user_response = client.get_user(username=username, user_fields=["created_at", "description"])
        if user_response.data is None:
            print(f"❌ No se encontró el usuario @{username}")
            return
        
        user_id = user_response.data.id
        print(f"✔ Usuario encontrado: ID {user_id} (@{username})")

        tweets_response = client.get_users_tweets(
            id=user_id,
            max_results=max_tweets,
            tweet_fields=["created_at", "public_metrics", "conversation_id"]
        )

        if not tweets_response.data:
            print("😶 No se encontraron tweets recientes.")
            return

        for tweet in tweets_response.data:
            print(f"\n📅 {tweet.created_at}")
            print(f"📝 {tweet.text}")
            print(f"❤️ {tweet.public_metrics['like_count']} | 🔁 {tweet.public_metrics['retweet_count']}")
            print("─" * 50)

            replies = get_top_replies(tweet.id, username)

            if replies:
                for idx, reply in enumerate(replies, 1):
                    print(f"  ↪️ RESPUESTA #{idx}")
                    print(f"  📝 {reply.text}")
                    print(f"  ❤️ {reply.public_metrics['like_count']} | 🔁 {reply.public_metrics['retweet_count']}")
                    print("  ─" * 25)
            else:
                print("  😴 Sin respuestas destacadas.")

    except tweepy.TweepyException as e:
        print(f"🚨 Error de Tweepy: {e}")
    except Exception as e:
        print(f"⚠ Error inesperado: {e}")

# 🚀 Ejecutar script
if __name__ == "__main__":
    debug_credentials()
    print("\nObteniendo tweets...")
    get_tweets("elonmusk", max_tweets=50)
