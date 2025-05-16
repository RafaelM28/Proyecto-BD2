import os
import tweepy
import streamlit as st
from dotenv import load_dotenv



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
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

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
                tweet_fields=["created_at", "public_metrics"]
            )

            tweets = response.data

            if not tweets:
                st.warning("⚠️ No se encontraron tweets.")
            else:
                for tweet in tweets:
                    st.markdown("---")
                    st.markdown(f"📅 **Fecha:** {tweet.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    st.markdown(f"📝 **Texto:** {tweet.text}")
                    st.markdown(f"❤️ **Likes:** {tweet.public_metrics['like_count']}")
        except tweepy.TweepyException as e:
            st.error(f"❌ Error en la API de Twitter: {e}")
