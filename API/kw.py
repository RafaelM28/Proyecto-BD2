import os
import tweepy
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime
from database.connector import MongoDBConnector
from sentiment_analysis import run_sentiment_analysis
from replies import get_tweets_with_top_replies

# =======================
# Credenciales (Rafael)
# =======================
client = tweepy.Client(
    bearer_token="AAAAAAAAAAAAAAAAAAAAAHBM1wEAAAAAdLT8muc6IEoWr9RjVrHDn7KgCbU%3DUJgOApG4Dl8miCHebrGc95bcBQC6OUeuf9jukCdQkoHSGRY6Hr",
    consumer_key="qgoaPW6q8f5C0xhFCT1ZvqgSH",
    consumer_secret="QZZGf3GPehvvgrukBWKiuv6jBJq9kVDaYw6uhZbz2MSvA42aiW",
    access_token="1162955265156816898-QrxEowUvmSpIYSKI5g2ovScmKj0AV5",
    access_token_secret="vismBF4LYx0PepuWOblGcN21feIRswyGxgeOEDf2lsJl0"
)

db_connector = MongoDBConnector()

# Configuración de Streamlit
st.set_page_config(page_title="Buscador de X", layout="wide")
st.title("🧠 Analizador de Posts de X (Twitter)")

tab1, tab2, tab3 = st.tabs(["🔍 Buscar Tweets", "📊 Análisis de Sentimientos", "💬 Respuestas Populares"])

# =======================
# REQ 1 - Buscar Tweets
# =======================
with tab1:
    st.subheader("🔍 Buscar y guardar tweets por palabra clave")

    keyword = st.text_input("Palabra clave", placeholder="Ej: inflación, elecciones")
    max_tweets = st.number_input("Máximo de post a traer", min_value=1, max_value=100, value=10)
    buscar = st.button("Buscar tweets")

    def transform_tweet_to_dict(tweet, keyword):
        return {
            "tweet_id": str(tweet.id),
            "text": tweet.text,
            "created_at": tweet.created_at,
            "author_id": str(tweet.author_id) if hasattr(tweet, 'author_id') else None,
            "public_metrics": {
                "like_count": tweet.public_metrics['like_count'],
                "retweet_count": tweet.public_metrics['retweet_count'],
                "reply_count": tweet.public_metrics.get('reply_count', 0),
                "impression_count": tweet.public_metrics.get('impression_count', 0)
            },
            "keyword": keyword,
            "source": "twitter_api",
            "inserted_at": datetime.now()
        }

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
                    for tweet in tweets:
                        data = transform_tweet_to_dict(tweet, keyword)
                        db_connector.insert_data("tweets", data)
                        st.markdown("---")
                        st.markdown(f"📅 **{tweet.created_at.strftime('%Y-%m-%d %H:%M:%S')}**")
                        st.markdown(f"📝 {tweet.text}")
                        st.markdown(f"❤️ Likes: {tweet.public_metrics['like_count']}")
                    st.success(f"✅ Se guardaron {len(tweets)} tweets.")
            except Exception as e:
                st.error(f"❌ Error al buscar tweets: {e}")

# =======================
# REQ 2 - Sentiment Analysis
# =======================
with tab2:
    st.subheader("📊 Análisis de sentimientos de los últimos tweets guardados")
    if st.button("Ejecutar análisis de sentimientos"):
        with st.spinner("Analizando..."):
            try:
                results = run_sentiment_analysis(limit=10)
                if not results:
                    st.warning("No hay tweets para analizar.")
                else:
                    for idx, res in enumerate(results, start=1):
                        st.markdown("---")
                        st.markdown(f"### 🐦 Tweet #{idx}")
                        st.markdown(f"**Texto:** {res['tweet']}")
                        st.markdown(f"**Palabra clave:** {res['keyword']}")
                        st.markdown("#### Resultado del análisis")
                        st.write("🧠 **Sentimiento:**", res["sentiment"].output, res["sentiment"].probas)
                        st.write("🎭 **Emoción:**", res["emotion"].output, res["emotion"].probas)
                        st.write("🧨 **Discurso de odio:**", res["hate_speech"].output, res["hate_speech"].probas)
                        st.write("⚠️ **Contexto de odio:**", res["context_hate"].output, res["context_hate"].probas)
            except Exception as e:
                st.error(f"❌ Error en el análisis: {e}")

# =======================
# REQ 3 - Respuestas Populares
# =======================
with tab3:
    st.subheader("💬 Respuestas más destacadas a un usuario")

    username = st.text_input("Usuario de X (sin @)", value="elonmusk")
    cantidad = st.slider("Cantidad de tweets recientes a analizar", 1, 10, 5)
    if st.button("Buscar respuestas populares"):
        with st.spinner("Buscando respuestas..."):
            try:
                tweets_info = get_tweets_with_top_replies(username, cantidad)
                if not tweets_info:
                    st.warning("⚠️ No se encontraron tweets o respuestas.")
                else:
                    for t in tweets_info:
                        st.markdown("----")
                        st.markdown(f"📝 **Tweet:** {t['text']}")
                        st.markdown(f"❤️ Likes: {t['likes']} | 🔁 Retweets: {t['retweets']}")
                        if t["replies"]:
                            st.markdown("#### Respuestas destacadas:")
                            for r in t["replies"]:
                                st.markdown(f"↪️ {r['text']}")
                                st.markdown(f"❤️ {r['likes']} | 🔁 {r['retweets']}")
                        else:
                            st.markdown("😴 Sin respuestas destacadas.")
            except Exception as e:
                st.error(f"❌ Error al buscar respuestas: {e}")
