import requests

API_URL = "stockx11.p.rapidapi.com/searchbykeyword" 
API_KEY = "API KEY HERE" 

Querystring = {"keyword": "jordan 1"}
headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "stockx11.p.rapidapi.com"
}

response = requests.get(API_URL, headers=headers, params=querystring)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")