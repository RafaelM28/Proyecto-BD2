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

# Función para convertir tweet a diccionario
def transform_tweet_to_dict(tweet, keyword):
    return {
        "tweet_id": str(tweet.id),
        "text": tweet.text,
        "created_at": tweet.created_at,
        "author_id": str(tweet.author_id) if hasattr(tweet, 'author_id') else None,
        "public_metrics": tweet.public_metrics,
        "keyword": keyword,
        "source": "twitter_api",
        "inserted_at": datetime.now()
    }

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
    except Exception as e:
        st.warning(f"⚠️ Error al obtener respuestas: {e}")
        return []

# Configurar página
st.set_page_config(page_title="Buscador y Análisis de Tweets", layout="centered")
st.title("🧠 Análisis de Contenido en Twitter")

tab1, tab2, tab3 = st.tabs(["🔍 Buscar Tweets", "🧪 Análisis de Sentimientos", "💬 Comentarios de un Tweet"])

# TAB 1 - Buscar y guardar tweets
with tab1:
    st.subheader("🔍 Búsqueda de Tweets por palabra clave")
    keyword = st.text_input("Palabra clave", placeholder="Ej: inflación, elecciones...")
    max_tweets = st.number_input("Número de tweets", min_value=1, max_value=100, value=10)
    buscar = st.button("Buscar y guardar")

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
                st.markdown(f"**Texto original:** {res['tweet']}")
                st.markdown(f"**Palabra clave:** {res['keyword']}")
                st.subheader("🔍 Resultados del Análisis")
                st.write("**Sentimiento:**", res["sentiment"].output, res["sentiment"].probas)
                st.write("**Emoción:**", res["emotion"].output, res["emotion"].probas)
                st.write("**Discurso de odio:**", res["hate_speech"].probas)
                st.write("**Contexto de odio:**", res["context_hate"].probas)

# TAB 3 - Mostrar comentarios de un tweet por ID
with tab3:
    st.subheader("💬 Comentarios de un Tweet específico")
    tweet_id_input = st.text_input("ID del Tweet", placeholder="Ejemplo: 1806831741287176413")
    show_replies = st.button("📬 Mostrar tweet y respuestas")

    if show_replies and tweet_id_input:
        try:
            tweet_response = client.get_tweet(
                id=tweet_id_input,
                tweet_fields=["created_at", "public_metrics", "author_id"]
            )
            tweet = tweet_response.data
            if tweet is None:
                st.warning("❌ No se encontró el tweet.")
            else:
                st.markdown("### 📝 Tweet principal")
                st.markdown(f"📅 {tweet.created_at}")
                st.markdown(f"📝 {tweet.text}")
                st.markdown(f"❤️ {tweet.public_metrics['like_count']} | 🔁 {tweet.public_metrics['retweet_count']}")
                st.markdown("---")

                replies = get_top_replies(tweet.id, max_replies=5)
                if replies:
                    st.markdown("### 💬 Respuestas destacadas")
                    for idx, reply in enumerate(replies, 1):
                        st.markdown(f"**↪️ Respuesta #{idx}**")
                        st.markdown(f"📝 {reply.text}")
                        st.markdown(f"❤️ {reply.public_metrics['like_count']} | 🔁 {reply.public_metrics['retweet_count']}")
                        st.markdown("---")
                else:
                    st.info("😶 No hay respuestas destacadas.")
        except Exception as e:
            st.error(f"⚠️ Error: {e}")
