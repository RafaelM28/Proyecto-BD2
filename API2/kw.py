import os
import tweepy
from dotenv import load_dotenv

# Cargar credenciales desde .env
load_dotenv("credencialesTwitter.env")

# Verificar credenciales
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

if not BEARER_TOKEN or not API_KEY or not API_SECRET or not ACCESS_TOKEN or not ACCESS_SECRET:
    print("❌ Error: Falta una o más credenciales en el archivo .env")
    exit() 

# Autenticación con Tweepy
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

# Función para buscar tweets originales por palabra clave
def search_tweets(keyword: str, max_tweets: int = 10):
    try:
        print(f"🔍 Buscando tweets originales con la palabra clave: {keyword}")

        # Agregar filtros para excluir respuestas y retweets
        query = f"{keyword} -is:reply -is:retweet"

        response = client.search_recent_tweets(
            query=query,
            max_results=max_tweets,
            tweet_fields=["created_at", "public_metrics"]
        )

        if not response.data:
            print("⚠️ No se encontraron tweets originales para esa palabra clave.")
            return
        
        for tweet in response.data:
            print(f"📅 {tweet.created_at}\n📝 {tweet.text}\n❤️ {tweet.public_metrics['like_count']} Likes\n---")

    except tweepy.TweepyException as e:
        print(f"❌ Error en la API: {e}")

# Ejemplo de uso
if __name__ == "__main__":
    search_tweets("guerra de aranceles", max_tweets=10)  # Cambia la palabra clave
