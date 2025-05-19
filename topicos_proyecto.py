import tweepy
import json
import time
from pysentimiento import create_analyzer
from pymongo import MongoClient  # Importar pymongo para conectarse a MongoDB

# Se crea una cuenta como desarrollador en X (antes Twitter) y se reemplaza con tu Bearer Token
bearer_token = "AAAAAAAAAAAAAAAAAAAAAGr70AEAAAAA5%2BgtYWJqdX2kiPk6lOjn3VwRTjo%3D6TweMDvCIBvFLtkND6XvzWRAhDjv2FSQTKoSrcRqhXn25tHd9H"

# Crear cliente con la API v2
client = tweepy.Client(bearer_token=bearer_token)

# Inicializa el analizador de sentimiento
analyzer = create_analyzer(task="sentiment", lang="es")

# Conexión a MongoDB Atlas
mongo_client = MongoClient("mongodb+srv://jacarrero22:fdGJLaVpqYHPZX26@cluster0.qrgnqoz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = mongo_client["topicos_especiales"]  # Nombre de la base de datos
collection = db["tweets"]  # Nombre de la colección

# Crear un índice único en el campo "id" para evitar duplicados
collection.create_index("id", unique=True)

# Obtener los últimos 10 tweets de una cuenta específica
def get_latest_tweets(username):
    try:
        time.sleep(5)  # Espera 5 segundos entre peticiones para evitar bloqueos

        user = client.get_user(username=username)
        user_id = user.data.id

        tweets = client.get_users_tweets(id=user_id, max_results=10)

        if tweets.data:
            for tweet in tweets.data:
                tweet_text = tweet.text

                # Analiza el sentimiento
                result = analyzer.predict(tweet_text)

                # Crear el documento para MongoDB
                tweet_document = {
                    "id": tweet.id,
                    "text": tweet_text,
                    "sentiment": result.output,  # 'POS', 'NEG', 'NEU'
                    "probs": result.probas,  # Probabilidades por clase
                    "username": username
                }

                # Insertar el documento en MongoDB (evitar duplicados con índice único)
                try:
                    collection.insert_one(tweet_document)
                    print(f"Tweet con ID {tweet.id} insertado en la base de datos.")
                except Exception as e:
                    print(f"Tweet con ID {tweet.id} ya existe en la base de datos. {e}")

            print(f"Tweets de @{username} analizados y guardados en la base de datos MongoDB.")
        else:
            print(f"No hay tweets recientes para @{username}.")

    except tweepy.TweepyException as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error general: {e}")

# Llamada a la función
get_latest_tweets("FCBarcelona_es")