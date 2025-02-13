import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch

def fetch_data_es(symbol = "BTC/USD"):
    # Connect to Elasticsearch
    es = Elasticsearch(["http://elasticsearch-cntr:9200"])


    # Define the time range (last 30 days)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=35)


    # Elasticsearch query for the last 30 days
    query = {
        "size": 10000,  
        "query": {
            "bool": {
                "must": [
                    {"term": {"symbol": symbol}},
                    {
                        "range": {
                            "t": {
                                "gte": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                "lte": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                "format": "yyyy-MM-dd'T'HH:mm:ss"
                            }
                        }
                    }
                ]
            }
        },
        "sort": [
            {"t": {"order": "asc"}}  # Change to "desc" for descending order
        ]
    }

    # Fetch data
    response = es.search(index="trading", body=query, scroll="2m")

    # Extract and format data
    hits = [hit["_source"] for hit in response["hits"]["hits"]]
    data = pd.DataFrame(hits)
    return data

def process_data(data):
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
    return data