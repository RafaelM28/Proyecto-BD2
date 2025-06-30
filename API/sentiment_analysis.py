from database.connector import MongoDBConnector
from pysentimiento import create_analyzer
from pysentimiento.preprocessing import preprocess_tweet
import transformers
from database.connector import MongoDBConnector
import spacy
from collections import Counter
import re

transformers.logging.set_verbosity(transformers.logging.ERROR)
db_connector = MongoDBConnector()
# Cargar modelo de español (ejecutar primero: python -m spacy download es_core_news_sm)
nlp = spacy.load("es_core_news_sm")

def transform_palabra_to_dict(palabra, frecuencia):
    """Convierte una palabra a un diccionario para MongoDB"""
    return {
        "palabra": str(palabra),
        "frecuencia": frecuencia,
    }
    
def palabras_frecuentes_spacy(oraciones, n=6,excluir_stopwords=True):
    # Compilar patrones de exclusión una sola vez
    patron_no_deseado = re.compile(r'^[\.#,_\-]+$')
    patron_url = re.compile(r'https?://\S+|www\.\S+')
    
    # Procesamiento con pipeline de SpaCy
    palabras_validas = []
    for doc in nlp.pipe(oraciones, batch_size=50):
        for token in doc:
            # Determinar la forma de la palabra a usar
            palabra = token.lemma_.lower()
            
            # Aplicar todos los filtros
            if (token.is_alpha and
                len(token.text) >= 3 and
                not patron_no_deseado.match(token.text) and
                not patron_url.fullmatch(token.text)):
                
                if not (excluir_stopwords and token.is_stop):
                    palabras_validas.append(palabra)
    
    for palabra, frecuencia in Counter(palabras_validas).most_common(n):
        try:
            palabra_dict = transform_palabra_to_dict(palabra, frecuencia)
            db_connector.insert_data("palabras_comunes", palabra_dict)
        except Exception as e:
            print(f"Error al insertar palabra {palabra}: {e}")
            
def hashtags_mas_comunes(oraciones, n=5):
    """
    Encuentra los hashtags más comunes en un conjunto de oraciones
    
    Args:
        oraciones (list): Lista de strings con las oraciones a analizar
        n (int): Número de hashtags más comunes a devolver
    
    Returns:
        Lista de tuplas (hashtag, frecuencia) ordenadas por frecuencia descendente
    """
    hashtags = []
    
    # Patrón mejorado para hashtags:
    # - Permite caracteres internacionales
    # - Excluye puntuación adyacente
    # - No captura URLs/menciones
    patron_hashtag = re.compile(
        r'(?<!\w)#([a-zA-Z0-9áéíóúüñÁÉÍÓÚÜÑ_\-]+)(?![@\w])', 
        re.UNICODE
    )
    
    for texto in oraciones:
        hashtags_encontrados = patron_hashtag.findall(texto.lower())
        
        for ht in hashtags_encontrados:
            # Validación adicional
            if ht and not ht.isdigit() and len(ht) >= 2:  # Longitud mínima de 2 caracteres
                hashtags.append(f"#{ht}")  # Reconstruimos el hashtag
    
    for hashtag, frecuencia in Counter(hashtags).most_common(n):
        try:
            hashtag_dict = transform_palabra_to_dict(hashtag, frecuencia)
            db_connector.insert_data("hashtags_comunes", hashtag_dict)
        except Exception as e:
            print(f"Error al insertar hashtag {hashtag}: {e}")
            
def run_sentiment_analysis(limit=30):
    db_connector = MongoDBConnector()

    try:
        tweets = db_connector.find_data("tweets", limit=limit)
        oraciones = [tweet["text"] for tweet in tweets if "text" in tweet]
    except Exception as e:
        raise RuntimeError(f"Error fetching tweets: {e}")

    if not tweets:
        return []

    # Guardar en la BD las palabras y hashtags más frecuentes en los tweets
    palabras_frecuentes_spacy(oraciones)
    hashtags_mas_comunes(oraciones)
    
    # Análisis de sentimientos  
    sentiment_analyzer = create_analyzer(task="sentiment", lang="es")
    emotion_analyzer = create_analyzer(task="emotion", lang="es")
    hate_speech_analyzer = create_analyzer(task="hate_speech", lang="es")
    context_analyzer = create_analyzer("context_hate_speech", lang="es")

    results = []
    for idx, tweet in enumerate(tweets, 1):
        if "text" in tweet and "keyword" in tweet:
            text = preprocess_tweet(tweet["text"])

            result = {
                "tweet": tweet["text"],
                "sentiment": sentiment_analyzer.predict(text),
                "emotion": emotion_analyzer.predict(text),
                "hate_speech": hate_speech_analyzer.predict(text),
                "context_hate": context_analyzer.predict(text, context=tweet["keyword"]),
                "keyword": tweet["keyword"],
            }
            
            result_bd = {
                "tweet": tweet["text"],
                "sentiment": result["sentiment"].probas,
                "emotion": result["emotion"].probas,
                "hate_speech": result["hate_speech"].probas,
                "context_hate": result["context_hate"].probas,
                "keyword": tweet["keyword"],
                "emotion_output": result["emotion"].output,
            }
            try:
                db_connector.insert_data("analisis_sentimientos", result_bd)
            except Exception as e:
                print(f"Error inserting analysis for tweet {idx}: {e}")
                continue
            results.append(result)

    return results