from prophet import Prophet
import pandas as pd


def get_exog_vars(target):
    """
    Sélectionne dynamiquement les variables exogènes en fonction de la variable cible.
    """
    features = {
        'c': ['o', 'h', 'l', 'v', 'volatilite', 'rolling_mean_24h', 'rolling_std_24h', 'spread', 'log_return'],
        'o': ['c', 'h', 'l', 'v', 'volatilite', 'rolling_mean_24h', 'rolling_std_24h', 'spread', 'log_return'],
        'h': ['o', 'c', 'l', 'v', 'volatilite', 'rolling_mean_24h', 'rolling_std_24h', 'spread', 'log_return'],
        'l': ['o', 'h', 'c', 'v', 'volatilite', 'rolling_mean_24h', 'rolling_std_24h', 'spread', 'log_return'],
        'v': ['o', 'h', 'c', 'l', 'volatilite', 'rolling_mean_24h', 'rolling_std_24h', 'spread', 'log_return'],

    }
    return features.get(target, [])

def train_prophet(train_data, target='c'):
    """
    Entraîne un modèle Prophet sur les données fournies.

    Paramètres :
    - train_data : DataFrame contenant la série temporelle et les features exogènes.
    - target : La variable cible pour l'entraînement ('c', 'o', etc.).

    Retourne :
    - Le modèle Prophet entraîné
    """
    exog_vars = get_exog_vars(target)

    # Vérifier si la colonne de timestamp existe
    timestamp_col = 't' if 't' in train_data.columns else 'timestamp'
    train_data = train_data.copy()  # Éviter les warnings SettingWithCopyWarning
    train_data[timestamp_col] = pd.to_datetime(train_data[timestamp_col]).dt.tz_localize(None)

    # Préparer les données pour Prophet
    prophet_data = train_data[[timestamp_col, target]].rename(columns={timestamp_col: 'ds', target: 'y'})

    # Ajouter les variables exogènes
    for var in exog_vars:
        if var in train_data.columns:
            prophet_data[var] = train_data[var]

    # Définition du modèle
    model = Prophet()

    # Ajouter les régressseurs exogènes au modèle
    for var in exog_vars:
        if var in train_data.columns:
            model.add_regressor(var)

    # Entraînement du modèle
    try:
        model.fit(prophet_data)
    except Exception as e:
        print(f"Erreur lors de l'entraînement du modèle Prophet : {e}")
        return None

    return model

def evaluate_prophet(model, test_data, target='c'):
    """
    Évalue un modèle Prophet en faisant des prédictions et en calculant les métriques.

    Paramètres :
    - model : Modèle Prophet entraîné.
    - test_data : DataFrame contenant la série temporelle et les features exogènes.
    - target : La variable cible pour la prédiction ('c', 'o', etc.).

    Retourne :
    - Un DataFrame avec les valeurs réelles et prédites.
    """
    if model is None:
        print("Modèle non entraîné. Impossible d'évaluer.")
        return None

    exog_vars = get_exog_vars(target)

    # Vérifier si la colonne de timestamp existe
    timestamp_col = 't' if 't' in test_data.columns else 'timestamp'
    test_data = test_data.copy()  # Éviter SettingWithCopyWarning
    test_data[timestamp_col] = pd.to_datetime(test_data[timestamp_col]).dt.tz_localize(None)

    # Préparer les données de prévision
    future = test_data[[timestamp_col]].rename(columns={timestamp_col: 'ds'})

    # Ajouter les régressseurs exogènes
    for var in exog_vars:
        if var in test_data.columns:
            future[var] = test_data[var]

    # Faire les prédictions
    try:
        forecast = model.predict(future)
        test_data[target] = forecast['yhat'].values
    except Exception as e:
        print(f"Erreur lors de la prédiction : {e}")
        return None

    return test_data[[timestamp_col, target, target]]

def predict_prophet(model, data, target='c', forecast_hours=168):
    """
    Generates future predictions using a trained Prophet model.

    Parameters:
    - model: Trained Prophet model.
    - data: DataFrame with past observations and exogenous features.
    - target: The variable to predict.
    - forecast_hours: Number of hours to predict (default: 7 days).

    Returns:
    - A DataFrame with future timestamps and predictions.
    """
    if model is None:
        print("[Error] Model is not trained. Prediction aborted.")
        return None

    exog_vars = get_exog_vars(target)
    timestamp_col = 't' if 't' in data.columns else 'timestamp'

    data = data.copy()
    last_timestamp = pd.to_datetime(data[timestamp_col].max()).tz_localize(None)

    # Generate future timestamps
    future_dates = pd.date_range(start=last_timestamp, periods=forecast_hours, freq='H')
    future = pd.DataFrame({'ds': future_dates})

    # Fill exogenous variables with last available value
    for var in exog_vars:
        if var in data.columns:
            future[var] = data[var].iloc[-1]

    try:
        forecast = model.predict(future)
        future['ds'] = future['ds'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        future[target] = forecast['yhat'].values
    except Exception as e:
        print(f"[Error] Forecasting failed: {e}")
        return None, e

    return future[['ds', target]]