import os
import tweepy
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime
from database.connector import MongoDBConnector
from sentiment_analysis import run_sentiment_analysis

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

# Autenticación con Tweepy
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

# Conexión a MongoDB
db_connector = MongoDBConnector()

def transform_tweet_to_dict(tweet, keyword):
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
        "keyword": keyword,
        "source": "twitter_api",
        "inserted_at": datetime.now()
    }

# Interfaz de usuario
st.set_page_config(page_title="Buscador de Tweets", layout="centered")
st.title("🔍 Buscador de Post de X")

st.markdown("Ingresa una palabra clave para buscar tweets:")

keyword = st.text_input("Palabra clave", placeholder="Ej: guerra de aranceles")
max_tweets = st.number_input("Máximo de post a traer", min_value=1, max_value=100, value=10)
buscar = st.button("🔎 Buscar tweets")

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
                    tweet_data = transform_tweet_to_dict(tweet, keyword)
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

# Botón para análisis de sentimientos
analizar_sentimientos = st.button("Ejecutar Análisis de Sentimientos")

if analizar_sentimientos:
    st.info("Ejecutando análisis de sentimientos...")

    try:
        results = run_sentiment_analysis(limit=10)
    except Exception as e:
        st.error(f"Error al ejecutar el análisis: {e}")
        results = []

    if not results:
        st.warning("No hay tweets para analizar.")
    else:
        for idx, res in enumerate(results, start=1):
            st.markdown("---")
            st.markdown(f"### 🐦 Tweet X #{idx}")
            st.markdown(f"**Texto original:** {res['tweet']}")
            st.markdown(f"**Palabra clave:** {res['keyword']}")

            st.subheader("🔍 Resultados del Análisis")
            st.write("**Sentimiento:**", res["sentiment"].output, res["sentiment"].probas)
            st.write("**Emoción:**", res["emotion"].output, res["emotion"].probas)
            st.write("**Discurso de odio:**", res["hate_speech"].output, res["hate_speech"].probas)
            st.write("**Contexto de odio:**", res["context_hate"].output, res["context_hate"].probas)
