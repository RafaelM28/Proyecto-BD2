import os
import tweepy
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import time

load_dotenv()

# Configuración optimizada
client = tweepy.Client(
    # Aqui poner su bearer token
    bearer_token="AAAAAAAAAAAAAAAAAAAAAN7H0QEAAAAAbMJ0NX%2FHTS7M89dd6O%2FyEOvgmeI%3DYER0XSY4r2tlrXrM3TeetMIlt5kvoqL9O8RYsQTWl1tWyodReg"
)

def search_tweets(
    query: str,
    max_tweets: int = 5,
    days_ago: int = 7,
    include_retweets: bool = False,
    language: str = "es"
):
    """
    Busca tweets basados en parámetros avanzados
    
    Args:
        query: Términos de búsqueda (ej: "#USACHINA OR 'guerra comercial'")
        max_tweets: Máximo de tweets a retornar (10-100)
        days_ago: Búsqueda en los últimos X días (máx. 30 días para API gratuita)
        include_retweets: Incluir retweets en los resultados
        language: Código de idioma (es, en, etc.)
    """
    try:
        # Construcción de query avanzada
        search_query = f"{query} lang:{language}"
        if not include_retweets:
            search_query += " -is:retweet"

        # Obtener tweets
        tweets = client.search_recent_tweets(
            query=search_query,
            max_results=min(max_tweets, 100),  # Límite de la API
            tweet_fields=[
                "created_at", 
                "public_metrics", 
                "context_annotations",
                "entities"
            ],
            user_fields=["username", "verified"],
            expansions=["author_id"],
           start_time=datetime.now(timezone.utc) - timedelta(days=days_ago)
        )

        if not tweets.data:
            print("No se encontraron tweets con esos parámetros")
            return

        # Procesar resultados
        users = {u.id: u for u in tweets.includes['users']}
        
        for tweet in tweets.data:
            author = users[tweet.author_id]
            print("\n" + "═" * 50)
            print(f"🗨️ @{author.username} ({'✅' if author.verified else ''})")
            print(f"📅 {tweet.created_at}")
            print(f"❤️ {tweet.public_metrics['like_count']} likes | 🔁 {tweet.public_metrics['retweet_count']} RTs")
            print("\n" + tweet.text)
            
            # Mostrar hashtags si existen
            if hasattr(tweet, 'entities') and 'hashtags' in tweet.entities:
                print("\n🏷️ Hashtags:", ", ".join([h['tag'] for h in tweet.entities['hashtags']]))

    except tweepy.TweepyException as e:
        print(f"🚨 Error de Twitter API: {e}")
    except Exception as e:
        print(f"⚠️ Error inesperado: {e}")

if __name__ == "__main__":
    # Ejemplo de búsqueda para guerra comercial USA-China
    search_params = {
        "query": "(#USACHINA OR 'guerra comercial' OR 'conflicto comercial') (USA OR Estados Unidos) (China)",
        "max_tweets": 5,
        "days_ago": 10,
        "language": "es"
    }
    
    print("🔍 Buscando tweets sobre conflicto USA-China...")
    search_tweets(**search_params)
    time.sleep(5)