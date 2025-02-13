import requests

def fetch_crypto_bars(symbols, start_date, end_date):
    url = "https://data.alpaca.markets/v1beta3/crypto/us/bars"
    headers = {"accept": "application/json"}
    params = {
        "symbols": symbols,
        "timeframe": "1H",
        "start": start_date,
        "end": end_date,
        "limit": 25,
        "sort": "asc"
    }
    
    all_data = []
    next_page_token = None
    
    while True:
        if next_page_token:
            params["page_token"] = next_page_token
        
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        print(len(data["bars"].get(symbols, [])))
        
        if "bars" in data:
            all_data.extend(data["bars"].get(symbols, []))
        
        next_page_token = data.get("next_page_token")
        if not next_page_token:
            break
    
    return all_data

# Example usage
symbols = "BTC/USD"
start_date = "2024-02-01T00:00:00Z"
end_date = "2024-02-07T00:00:00Z"

crypto_bars = fetch_crypto_bars(symbols, start_date, end_date)
print(len(crypto_bars))  # Print the number of bars retrieved

print(crypto_bars)  # Print the bars retrieved