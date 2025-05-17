import os
import tweepy
import streamlit as st
from dotenv import load_dotenv
from database.connector import MongoDBConnector
from datetime import datetime


# Cargar credenciales
load_dotenv(".env")

BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

if not all([BEARER_TOKEN, API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
    st.error("❌ Error: Falta una o más credenciales en el archivo .env")
    st.stop()

# Autenticación
client = tweepy.Client(
    bearer_token="AAAAAAAAAAAAAAAAAAAAAN7H0QEAAAAAybgv%2FPYBlXykkvxZC3TQFVAv2WQ%3Dhc41yEFtBphbQZ025R8tg1pAGSXdJoI7qJSwhW3FpgCykBTihF",
    consumer_key="laZSmoXlGHHPMeEYZjiRSmJY2",
    consumer_secret="TVq9BYmAZwTA11lURLDqEZPx2Lk3lAP9E7HDX995EA0x3owSqx",
    access_token="739201544235683841-XG41v5IyOwvJRebjneiwhtKjiS1OU0b",
    access_token_secret="4Ky6EX0YxbMvqrkuOWf0XlaYFLGvoRTm0IIKhoPgvHFD8"
)

# Conexión a MongoDB
db_connector = MongoDBConnector()

def transform_tweet_to_dict(tweet):
    """Convierte un objeto Tweet a un diccionario para MongoDB"""
    return {
        "tweet_id": str(tweet.id),
        "text": tweet.text,
        "created_at": tweet.created_at,
        "author_id": str(tweet.author_id) if hasattr(tweet, 'author_id') else None,
        "public_metrics": {
            "like_count": tweet.public_metrics['like_count'],
            "retweet_count": tweet.public_metrics['retweet_count'],
            "reply_count": tweet.public_metrics['reply_count'],
            "impression_count": tweet.public_metrics['impression_count']
        },
        "keyword": keyword,  # Guardamos la palabra clave de búsqueda
        "source": "twitter_api",
        "inserted_at": datetime.now()
    }

# Interfaz de usuario
st.set_page_config(page_title="Buscador de Tweets", layout="centered")
st.title("🔍 Buscador de Post de X  🔍")

st.markdown("Ingresa una palabra clave para buscar tweets:")

keyword = st.text_input("Palabra clave", placeholder="Ej: guerra de aranceles")
max_tweets = st.number_input("Máximo de post a para traer", min_value=1, max_value=100, value=10)
buscar = st.button("Buscando Post en X 🔍")

# Resultado
if buscar and keyword:
    with st.spinner("Buscando tweets..."):
        try:
            query = f"{keyword} -is:reply -is:retweet lang:es"

            response = client.search_recent_tweets(
                query=query,
                max_results=max_tweets,
                tweet_fields=["created_at", "public_metrics", "author_id"],
                expansions=["author_id"]
            )

            tweets = response.data

            if not tweets:
                st.warning("⚠️ No se encontraron tweets.")
            else:
                inserted_ids = []
                for tweet in tweets:
                    # Transforma el tweet a diccionario
                    tweet_data = transform_tweet_to_dict(tweet)

                    # Inserta en MongoDB
                    try:
                        tweet_id = db_connector.insert_data("tweets", tweet_data)
                        inserted_ids.append(tweet_id)
                    except Exception as e:
                        st.error(f"Error al guardar tweet: {e}")
                        continue

                    st.markdown("---")
                    st.markdown(f"📅 **Fecha:** {tweet.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    st.markdown(f"📝 **Texto:** {tweet.text}")
                    st.markdown(f"❤️ **Likes:** {tweet.public_metrics['like_count']}")

                    st.success(f"✅ Se guardaron {len(inserted_ids)} tweets en la base de datos")
        except tweepy.TweepyException as e:
            st.error(f"❌ Error en la API de Twitter: {e}")
