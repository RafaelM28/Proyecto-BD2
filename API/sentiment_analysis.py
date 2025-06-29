from database.connector import MongoDBConnector
from pysentimiento import create_analyzer
from pysentimiento.preprocessing import preprocess_tweet
import transformers

transformers.logging.set_verbosity(transformers.logging.ERROR)

def run_sentiment_analysis(limit=10):
    db_connector = MongoDBConnector()

    try:
        tweets = db_connector.find_data("tweets", limit=limit)
    except Exception as e:
        raise RuntimeError(f"Error fetching tweets: {e}")

    if not tweets:
        return []

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
                "keyword": tweet["keyword"]
            }

            results.append(result)

    return results
