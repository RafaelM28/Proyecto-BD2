import os
import tweepy
from dotenv import load_dotenv

load_dotenv()

# Configuración optimizada
client = tweepy.Client(
    # Aqui poner su bearer token
    bearer_token=""
)

def debug_credentials():
    """Función para depuración de credenciales"""
    token = ""
    print(f"Token length: {len(token)} chars")
    print(f"Token starts with: {token[:10]}...")
    print(f"Token ends with: ...{token[-10:]}")
    print(f"Full token (hidden): {token[:5]}...{token[-5:]}")

def get_tweets(username: str, max_tweets: int = 5):
    try:
        # Paso 1: Obtener ID de usuario
        user_response = client.get_user(
            username=username,
            user_fields=["created_at", "description"]
        )
        
        if user_response.data is None:
            print(f"No se encontró el usuario @{username}")
            return
            
        user_id = user_response.data.id
        print(f"✔ Usuario encontrado: ID {user_id}")

        # Paso 2: Obtener tweets
        tweets_response = client.get_users_tweets(
            id=user_id,
            max_results=max_tweets,
            tweet_fields=["created_at", "public_metrics", "context_annotations"]
        )
        
        if tweets_response.data:
            for tweet in tweets_response.data:
                print(f"\n📅 {tweet.created_at}")
                print(f"🔢 Likes: {tweet.public_metrics['like_count']}")
                print(f"📝 {tweet.text}")
                print("-"*50)
        else:
            print("No se encontraron tweets recientes.")

    except tweepy.TweepyException as e:
        print(f"🚨 Error de Tweepy: {e}")
    except Exception as e:
        print(f"⚠ Error inesperado: {e}")

if __name__ == "__main__":
    debug_credentials()  # Verifica las credenciales primero
    print("\nObteniendo tweets...")
    get_tweets("elonmusk", max_tweets=5)