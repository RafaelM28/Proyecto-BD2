import os
import tweepy
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime
from database.connector import MongoDBConnector
from sentiment_analysis import run_sentiment_analysis

# Cargar variables de entorno
load_dotenv()
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Verificación de credenciales
if not all([BEARER_TOKEN, API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
    st.error("❌ Faltan credenciales en el archivo .env")
    st.stop()

# Cliente Tweepy
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

# Conexión a MongoDB
db_connector = MongoDBConnector()

# Función para obtener respuestas destacadas
def get_top_replies(tweet_id: str, max_replies: int = 5):
    query = f"conversation_id:{tweet_id} is:reply"
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
        return sorted(
            replies,
            key=lambda r: r.public_metrics.get("like_count", 0) + r.public_metrics.get("retweet_count", 0),
            reverse=True
        )[:max_replies]
    except Exception:
        return []

# Función para convertir tweet a diccionario con replies
def transform_tweet_to_dict(tweet, keyword):
    top_replies = get_top_replies(tweet.id, max_replies=3)
    reply_dicts = [{
        "text": r.text,
        "created_at": r.created_at,
        "like_count": r.public_metrics.get("like_count", 0),
        "retweet_count": r.public_metrics.get("retweet_count", 0)
    } for r in top_replies]

    return {
        "tweet_id": str(tweet.id),
        "text": tweet.text,
        "created_at": tweet.created_at,
        "author_id": str(tweet.author_id) if hasattr(tweet, 'author_id') else None,
        "public_metrics": tweet.public_metrics,
        "keyword": keyword,
        "replies": reply_dicts,
        "inserted_at": datetime.now()
    }

# Configurar página
st.set_page_config(page_title="Buscador y Análisis de Tweets", layout="centered")
st.title("🧠 Análisis de Contenido en Twitter")

tab1, tab2 = st.tabs(["🔍 Buscar Tweets", "🧪 Análisis de Sentimientos"])

# TAB 1 - Buscar y mostrar tweets con comentarios
with tab1:
    st.subheader("🔍 Búsqueda de Tweets por palabra clave")
    keyword = st.text_input("Palabra clave", placeholder="Ej: inflación, elecciones...")
    max_tweets = st.number_input("Número de tweets", min_value=1, max_value=100, value=5)
    buscar = st.button("Buscar y mostrar")

    if buscar and keyword:
        with st.spinner("Buscando tweets..."):
            try:
                query = f"{keyword} -is:reply -is:retweet lang:es"
                response = client.search_recent_tweets(
                    query=query,
                    max_results=max_tweets,
                    tweet_fields=["created_at", "public_metrics", "author_id"]
                )
                tweets = response.data

                if not tweets:
                    st.warning("⚠ No se encontraron tweets.")
                else:
                    for tweet in tweets:
                        tweet_data = transform_tweet_to_dict(tweet, keyword)
                        try:
                            db_connector.insert_data("tweets", tweet_data)
                        except Exception as e:
                            st.error(f"Error al guardar tweet: {e}")
                            continue

                        st.markdown("### 🐦 Tweet")
                        st.markdown(f"📅 {tweet_data['created_at']}")
                        st.markdown(f"📝 {tweet_data['text']}")
                        st.markdown(f"❤ {tweet_data['public_metrics']['like_count']} | 🔁 {tweet_data['public_metrics']['retweet_count']}")
                        st.markdown("---")

                        replies = tweet_data["replies"]
                        if replies:
                            st.markdown("#### 💬 Comentarios destacados")
                            for i, reply in enumerate(replies, 1):
                                st.markdown(f"#{i}** {reply['text']}")
                                st.markdown(f"❤ {reply['like_count']} | 🔁 {reply['retweet_count']}")
                                st.markdown("—")
                        else:
                            st.info("😶 Sin comentarios destacados.")
                        st.markdown("===")
            except tweepy.TweepyException as e:
                st.error(f"❌ Error en la API de Twitter: {e}")

# TAB 2 - Análisis de sentimientos
with tab2:
    st.subheader("🧪 Análisis de Sentimientos")
    analizar = st.button("Ejecutar análisis")

    if analizar:
        st.info("Ejecutando análisis de sentimientos...")
        try:
            results = run_sentiment_analysis(limit=10)
        except Exception as e:
            st.error(f"Error: {e}")
            results = []

        if not results:
            st.warning("No hay tweets para analizar.")
        else:
            for idx, res in enumerate(results, 1):
                st.markdown("---")
                st.markdown(f"### 🐦 Tweet #{idx}")
                st.markdown(f"*Texto original:* {res['tweet']}")
                st.markdown(f"*Palabra clave:* {res['keyword']}")
                st.subheader("🔍 Resultados del Análisis")
                st.write("*Sentimiento:*", res["sentiment"].output, res["sentiment"].probas)
                st.write("*Emoción:*", res["emotion"].output, res["emotion"].probas)
                st.write("*Discurso de odio:*", res["hate_speech"].probas)
                st.write("*Contexto de odio:*", res["context_hate"].probas)