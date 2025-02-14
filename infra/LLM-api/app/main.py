from fastapi import FastAPI, HTTPException
from elasticsearch import Elasticsearch
import pandas as pd
import random
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer

# 🔹 Initialisation de FastAPI
app = FastAPI()

# 🔹 Connexion à Elasticsearch
es = Elasticsearch("http://localhost:9200")  # Remplace par ton URL Elasticsearch

# 🔹 Chargement du modèle GPT-2 pour générer des recommandations
model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
text_generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

# 🔹 Recommandations de secours si GPT-2 ne génère pas un bon résultat
recommendations_dict = {
    "positive": [
        "Consider buying Bitcoin while the trend remains strong.", 
        "Hold your Bitcoin and wait for higher gains.", 
        "Accumulate Bitcoin gradually for long-term profits."
    ],
    "neutral": [
        "Monitor Bitcoin's price before making a decision.", 
        "Stay cautious and wait for a clearer trend.", 
        "Avoid major trades until a new trend emerges."
    ],
    "negative": [
        "Consider selling Bitcoin to minimize risk.", 
        "Wait before making new investments in Bitcoin.", 
        "Avoid Bitcoin trading until the market stabilizes."
    ]
}

# 🔹 Seuils de variation pour classer le sentiment
THRESHOLD_UP = 0.5   
THRESHOLD_DOWN = -0.5 

def classify_sentiment(variation):
    """Détecte le sentiment du marché en fonction de la variation du prix."""
    if variation >= THRESHOLD_UP:
        return "positive"
    elif variation <= THRESHOLD_DOWN:
        return "negative"
    else:
        return "neutral"

def generate_recommendation(symbol, sentiment, variation):
    """Génère une recommandation de trading basée sur le sentiment."""
    prompt = f"Bitcoin ({symbol}) has a {sentiment} trend with a variation of {variation:.2f}. Recommended action:"

    output = text_generator(prompt, max_length=len(prompt.split()) + 60, num_return_sequences=1, truncation=True)
    recommendation = output[0]["generated_text"].replace(prompt, "").strip().split(".")[0] + "."

    # Vérifier si la recommandation contient un mot-clé pertinent
    valid_keywords = ["buy", "sell", "hold", "wait", "accumulate", "avoid", "monitor", "watch"]
    if not any(word in recommendation.lower() for word in valid_keywords):
        recommendation = random.choice(recommendations_dict[sentiment])

    return recommendation

@app.get("/analyze/{es_id}")
def analyze_trade(es_id: str):
    """Endpoint FastAPI pour analyser un trade et donner une recommandation."""
    
    # 🔹 Requête Elasticsearch pour récupérer les données du trade
    response = es.get(index="trading", id=es_id, ignore=404)
    
    if not response or "_source" not in response:
        raise HTTPException(status_code=404, detail="Trade not found in Elasticsearch")

    data = response["_source"]
    
    # 🔹 Calcul de la variation du prix
    variation = data["c"] - data["o"]
    
    # 🔹 Détection du sentiment du marché
    sentiment = classify_sentiment(variation)
    
    # 🔹 Génération de la recommandation
    recommendation = generate_recommendation(data["symbol"], sentiment, variation)

    # 🔹 Résultat final
    result = {
        "es_id": es_id,
        "symbol": data["symbol"],
        "timestamp": data["t"],
        "open": data["o"],
        "close": data["c"],
        "variation": variation,
        "sentiment": sentiment,
        "recommendation": recommendation
    }
    
    return result

# 🔹 Pour exécuter l'API :
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload
