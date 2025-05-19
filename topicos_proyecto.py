from flask import Flask, render_template, request, redirect, url_for, flash
import tweepy
import json
import time
from pymongo import MongoClient
from pysentimiento import create_analyzer

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necesario para usar flash (mensajes)

# ==== CONFIGURACIÓN DE TWITTER ====
bearer_token = "AAAAAAAAAAAAAAAAAAAAAGr70AEAAAAA5%2BgtYWJqdX2kiPk6lOjn3VwRTjo%3D6TweMDvCIBvFLtkND6XvzWRAhDjv2FSQTKoSrcRqhXn25tHd9H"
client = tweepy.Client(bearer_token=bearer_token)

# ==== CONFIGURACIÓN DE MONGODB ====
mongo_uri = "mongodb://localhost:27017"
mongo_client = MongoClient(mongo_uri)
db = mongo_client["twitter_db"]
collection = db["tweets_sentimiento"]

# ==== ANALIZADOR DE SENTIMIENTO ====
analyzer = create_analyzer(task="sentiment", lang="es")

# ==== FUNCION PARA OBTENER Y GUARDAR TWEETS ====
def get_latest_tweets(username):
    time.sleep(5)  # Evitar bloqueos

    user = client.get_user(username=username)
    user_id = user.data.id
    tweets = client.get_users_tweets(id=user_id, max_results=10)

    if tweets.data:
        tweets_data = []

        for tweet in tweets.data:
            tweet_text = tweet.text
            result = analyzer.predict(tweet_text)

            tweet_doc = {
                "id": tweet.id,
                "username": username,
                "text": tweet_text,
                "sentiment": result.output,
                "probs": dict(result.probas)
            }
            tweets_data.append(tweet_doc)

        collection.insert_many(tweets_data)
        return True
    else:
        return False

# ==== LISTA DE CUENTAS ====
cuentas = {
    "Real Madrid": "realmadrid",
    "FC Barcelona": "FCBarcelona",
    "Athletic Club": "AthleticClub",
    "Atlético de Madrid": "Atleti",
    "Club deportivo leganés": "CDLeganes",
    "Villarreal CF": "VillarrealCF",
    "Real Sociedad": "RealSociedad",
    "Sevilla FC": "SevillaFC",
    "Real Betis": "RealBetis",
    "Valencia CF": "valenciacf"
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        cuenta = request.form.get("cuenta")
        username = cuentas.get(cuenta)
        if username:
            success = get_latest_tweets(username)
            if success:
                flash(f"Tweets de @{username} guardados exitosamente.", "success")
            else:
                flash(f"No se encontraron tweets para @{username}.", "warning")
        else:
            flash("Cuenta no válida.", "danger")
        return redirect(url_for("index"))
    return render_template("index.html", cuentas=cuentas.keys())

if __name__ == "__main__":
    app.run(debug=True)
