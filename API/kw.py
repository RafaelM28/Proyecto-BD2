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
    
    """ CREDENCIALES PEDRO UCAB
    bearer_token="AAAAAAAAAAAAAAAAAAAAAIo71wEAAAAAG2C6I0BT4xUD2dnSAqVf9mPMmTQ%3DAxBaCtj2VInuN4GkUidy4FjgHO1c53BbrhoA1SeP2kKyTpSYO8",
    consumer_key="CScF43Cp29qhWtLi8dHxK8IvD",
    consumer_secret="5A49kX6tXFFxqzb4GCtaVmB8Pt5GNR3MCC8dl7SQ7FffqoxCTU",
    access_token="1923903042828603392-IruX2ZsriOetZvf47d3Hc41TcDu7xR",
    access_token_secret="1XdRd8yfSvPQgKdvI7GiV0RccIZwOqCldzhk8tryY8btN"
    """

    """bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
    """
# Autenticación
client = tweepy.Client(
    bearer_token="AAAAAAAAAAAAAAAAAAAAAPco1AEAAAAA92B%2Bt3aTXPdiiF%2BVTkPMJnFrboI%3D5VoiNqB0mZsBWLFUZycUEm2B2VscN5DXnbYVEZ9WF5dy829E51",
    consumer_key="yWiERIm2Ed9GWMbq8bg0UR3XY",
    consumer_secret="NnaHT23ZmRUFPAEJHKSanU6kw2vsUYD2R3QlkhA3z2sBcvLjYX",
    access_token="2872126068-TE7SgvSCHZQVFmiPNrPKIX9613ImbWtN0pZLc8A",
    access_token_secret="KilJoV0V0tQbsQGt1J3ReUOSPg241GC3uQaQF897ZifPL"
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
