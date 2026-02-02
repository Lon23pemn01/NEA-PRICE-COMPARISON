import requests

def search_stockx_gb(api_key, query, country='GB', locale='en-GB', currency='GBP'):
   
    url = "https://piloterr.com/api/v2/stockx/product"
    
    headers = {
        "x-api-key": api_key
    }
    
    params = {
        "query": query,
        "country": country,
        "locale": locale,
        "currency": currency
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        market = data.get('market', {})
        bids = market.get('bids', {})
        
        print(f"Product: {data.get('name')}")
        print(f"Lowest Ask: £{bids.get('lowest_ask')}")
        print(f"Highest Bid: £{bids.get('highest_bid')}")
        print(f"Last Sale: £{market.get('sales', {}).get('last_sale')}")
        
        return data

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

if __name__ == "__main__":
    search_stockx_gb("b17cbfd9-9e90-4f3c-bdd7-51bf35b74139", "air-jordan-4-retro-rare-air-white-lettering")