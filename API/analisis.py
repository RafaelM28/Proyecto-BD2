from database.connector import MongoDBConnector
from pysentimiento import create_analyzer
import transformers
from pysentimiento.preprocessing import preprocess_tweet

# Esta librería solo es utilizada para fines de mostrar los análisis de los modelos en la terminal
# No es necesario para el funcionamiento del código
from pprint import pprint

# Desactiva las advertencias de la librería transfomers para solo mostrar errores
transformers.logging.set_verbosity(transformers.logging.ERROR)

# Conexión a MongoDB 
db_connector = MongoDBConnector()

# Establecemos conexión a la BD y creamos la lista (colección) de Tweets
tweets = db_connector.find_data("Tweets", limit=10)
try:
    db_connector.find_data("Tweets")
except Exception as e:
    print(f"An error occurred while fetching data: {e}")

''' Las siguientes lineas de código de formato de impresión solo son necesarias para fines visuales en la terminal
    y no afectan el funcionamiento del código''' 
# Recorremos la lista de tweets y analizamos cada uno
for idx, tweet in enumerate(tweets, 1):
    if ("text" in tweet) and ("keyword" in tweet):
        print("\n" + "="*60)
        print(f"TWEET #{idx}")
        print("="*60)
        print("Texto original:")
        print(tweet["text"])
        text = preprocess_tweet(tweet["text"])

        print("\n[Análisis de reacciones (neutral, positivo, negativo)]")
        analyzer = create_analyzer(task="sentiment", lang="es")
        pprint(analyzer.predict(text))

        print("\n[Análisis de emociones]")
        emotion_analyzer = create_analyzer(task="emotion", lang="es")
        pprint(emotion_analyzer.predict(text))

        print("\n[Análisis de odio]")
        hate_speech_analyzer = create_analyzer(task="hate_speech", lang="es")
        pprint(hate_speech_analyzer.predict(text))

        print("\n[Análisis de contexto de odio (el porqué sucede. Utiliza como contexto el keyword/palabras clave)]")
        analyzer = create_analyzer("context_hate_speech", lang="es")
        pprint(analyzer.predict(
            text,
            context = tweet["keyword"],
        ))
    else:
        print("No se encontró el campo 'text' en el tweet.")
        text = None
        