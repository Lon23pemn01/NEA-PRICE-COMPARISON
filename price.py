import requests

def search_stockx_gb(api_key, query, country='GB', locale='en-GB', currency='GBP'):

API_URL = "stockx11.p.rapidapi.com/searchbykeyword"
API_KEY = "API Key HERE"

headers = {"Authorization": f"Bearer {API_KEY}"}
params = {"query": "Jordan 1"}

response = requests.get(API_URL, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()
    
    print(f"Found {data['meta']['total']} products\n")
    
    for product in data["data"][:5]: 
        print(f"• {product['title']}")
        print(f"  SKU: {product['sku']}")
        print(f"  Price: ${product['min_price']} - ${product['max_price']}\n")

return data

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

else:
    print(f"Error: {response.status_code}")