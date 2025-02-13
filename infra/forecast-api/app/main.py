import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from utils.es_utils import fetch_data_es, process_data
from utils.prophet_utils import train_prophet, predict_prophet

app = Flask(__name__)

# ----------- Utilisation -----------


@app.route('/forecast_data', methods=['GET'])
def forecast_data():

    # Récupération du symbole
    symbol = request.args.get('symbol')

    # Récupération des données
    data = fetch_data_es(symbol)
    data = process_data(data)

    # Nettoyage des données
    data.replace([np.inf, -np.inf], np.nan, inplace=True)
    data.dropna(inplace=True)

    # Vérifier si la colonne timestamp existe
    timestamp_col = 't' if 't' in data.columns else 'timestamp'
    data = data.copy()  # Éviter SettingWithCopyWarning
    data[timestamp_col] = pd.to_datetime(data[timestamp_col]).dt.tz_localize(None)

    # Définition des périodes d'entraînement et de test en heures
    train_hours = 30 * 24  # 30 jours en heures
    forecast_hours = 7 * 24  # 7 jours en heures
    train = data.iloc[-(train_hours + forecast_hours):-forecast_hours].copy()
    test = data.iloc[-forecast_hours:].copy()

    # Sélection de la variable cible
    # target_variables = 'h'  # 'c', 'o', etc.
    target_variables = ['h', 'c', 'o', 'l', 'v']

    all_results = []  # Liste pour stocker les résultats des prédictions


    for target_variable in target_variables:
        # Entraînement du modèle
        prophet_model = train_prophet(train, target=target_variable)

        # # Évaluation et affichage des résultats
        # if prophet_model:
        #     # Évaluation sur les données de test (optionnel)
        #     evaluate_prophet(prophet_model, test, target=target_variable)

        # Prédictions pour la période de 7 jours
        results = predict_prophet(prophet_model, data, target_variable)

        if isinstance(results, tuple):
            return jsonify({"error": results[1]})
        
        if results is not None:
            # Ajouter les résultats dans la liste
            all_results.append(results[['ds', target_variable]])

    # Fusionner tous les résultats basés sur le timestamp 'ds'
    if all_results:
        merged_results = all_results[0]
        for result in all_results[1:]:
            merged_results = merged_results.merge(result, on='ds', how='outer')

        
        merged_results = merged_results.round(4)

        # Afficher les résultats fusionnés (optionnel)
        print(merged_results)

        return jsonify(merged_results.to_dict(orient='records'))
    else:
        return jsonify({"error": "No predictions were made"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)