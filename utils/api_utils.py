import requests


def get_data(symbols, start_date, end_date="2025-02-08T00:00:00Z", limit=1000):
    url = "https://data.alpaca.markets/v1beta3/crypto/us/bars"
    headers = {"accept": "application/json"}
    params = {
        "symbols": symbols,
        "timeframe": "1H",
        "start": start_date,
        "end": end_date,
        "limit": limit,
        "sort": "asc"
    }

    all_data = {}
    next_page_token = None

    while True:
        if next_page_token:
            params["page_token"] = next_page_token
        
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"API Error: {response.status_code} - {response.text}")
            break  # Stop the loop on API error

        data = response.json()
        print(len(data["bars"].get(symbols.split(',')[0], [])) + len(data["bars"].get(symbols.split(',')[1], [])))

        if "bars" not in data:
            print(f"Unexpected API Response: {data}")
            break  # Stop the loop if 'bars' is missing

        for symbol, bars in data["bars"].items():
            all_data.setdefault(symbol, []).extend(bars)  # More efficient way to extend lists

        next_page_token = data.get("next_page_token")
        if not next_page_token:
            break  # Stop fetching when no next page

    return all_data


# Iterate through each symbol in the data and add the symbol to each individual entry
def format_data(raw_data):
    formatted_data = []
    for symbol, bars in raw_data.items():
        for bar in bars:
            bar['symbol'] = symbol  # Add the symbol to each entry
            formatted_data.append(bar)
    
    # Now, formatted_data contains entries with the symbol included
    return formatted_data