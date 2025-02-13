import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error, mean_squared_error


# Load the data

data=pd.read_csv("crypto_data.csv")

# Data preprocessing

data['market'] = data['c'] * data['v']
# close -> log_close
data['volatilite'] = data['h'] - data['l']
# market -> log_market
#crypto['log_market'] = np.log(crypto.market)
data['log_market'] = np.log(data.market)
data['rolling_mean_24h'] = data['c'].rolling(window=24, min_periods=1).mean()
data['rolling_std_24h'] = data['c'].rolling(window=24, min_periods=1).std()

# Spread
data['spread'] = (data.h - data.l) / data.c
# return -> log (close / open)
data['log_return'] = np.log(data.c / data.c.shift(1))

data.dropna(inplace=True)



# Functionalities



def get_exog_vars(target):
    """
    Sélectionne les variables exogènes en fonction de la variable cible.
    
    Paramètre :
    - target : La colonne cible ('c', 'o', etc.)
    
    Retourne :
    - Liste des variables exogènes correspondantes
    """
    features = ['o','c', 'h', 'l', 'v', 'volatilite', 'rolling_mean_24h', 'rolling_std_24h', 'spread', 'log_return']
    return [f for f in features if f != target]  # Exclure la target des exogènes


def train_arima(train_data, target='c', order=(2,1,2)):
    """
    Entraîne un modèle ARIMA sur les données fournies.

    Paramètres :
    - train_data : DataFrame contenant la série temporelle et les features exogènes.
    - target : La variable cible pour l'entraînement ('c', 'o', etc.).
    - order : Tuple (p,d,q) pour la configuration d'ARIMA.

    Retourne :
    - Le modèle entraîné
    """
    exog_vars = get_exog_vars(target)  # Sélection dynamique des variables exogènes

    arima_model = ARIMA(train_data[target], order=order, exog=train_data[exog_vars])
    arima_fit = arima_model.fit()
    
    return arima_fit


def evaluate_arima(model, test_data, target='c'):
    """
    Évalue un modèle ARIMA en faisant des prédictions et en calculant les métriques.

    Paramètres :
    - model : Modèle ARIMA entraîné.
    - test_data : DataFrame contenant la série temporelle et les features exogènes.
    - target : La variable cible pour la prédiction ('c', 'o', etc.).

    Retourne :
    - Un DataFrame avec les valeurs réelles et prédites.
    - Affiche les métriques et un graphique.
    """
    exog_vars = get_exog_vars(target)  # Sélection dynamique des variables exogènes

    # Prédiction sur la période test
    arima_pred = model.forecast(steps=len(test_data), exog=test_data[exog_vars])
    
    # Ajout des prédictions dans le DataFrame test
    test_data = test_data.copy()  # Éviter SettingWithCopyWarning
    test_data['arima_pred'] = arima_pred.values

    # Calcul des métriques d’évaluation
    mae = mean_absolute_error(test_data[target], test_data['arima_pred'])
    rmse = np.sqrt(mean_squared_error(test_data[target], test_data['arima_pred']))
    mape = np.mean(np.abs((test_data[target] - test_data['arima_pred']) / test_data[target])) * 100

    # Affichage des métriques
    metrics_results = pd.DataFrame({
        "Model": ["ARIMA"],
        "Target": [target],
        "MAE": [mae],
        "RMSE": [rmse],
        "MAPE (%)": [mape],
    })

    print(metrics_results)

    # Tracé des résultats
    plt.figure(figsize=(12, 6))
    plt.plot(test_data.index, test_data[target], marker='o', linestyle='-', label=f'Valeurs réelles ({target})')
    plt.plot(test_data.index, test_data['arima_pred'], marker='o', linestyle='--', label='Prédictions ARIMA', color='red')

    plt.xlabel("Date et Heure")
    plt.ylabel(f"Valeur de {target}")
    plt.title(f"Prédiction ARIMA sur {len(test_data)} heures ({target})")
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid()
    plt.show()

    return test_data[[target, 'arima_pred']]


# ----------- Utilisation -----------

# Nettoyage des données
data.dropna(inplace=True)
data.replace([np.inf, -np.inf], np.nan, inplace=True)
data.dropna(inplace=True)

# Définition des périodes d'entraînement et de test en heures
train_hours = 30 * 24  # 30 jours en heures
forecast_hours = 7 * 24  # 7 jours en heures
train = data.iloc[-(train_hours + forecast_hours):-forecast_hours]
test = data.iloc[-forecast_hours:]

# Sélection de la variable cible
target_variable = 'h'  # 'c', 'o', etc.

# Entraînement du modèle
arima_model = train_arima(train, target=target_variable)

# Évaluation et affichage des résultats
results = evaluate_arima(arima_model, test, target=target_variable)
print(results)
