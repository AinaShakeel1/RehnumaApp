import requests
from bs4 import BeautifulSoup
import json

url = "https://www.naheed.pk/banana-local-1-dozen"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Extract from JSON-LD script
product_data = {}
for script in soup.find_all("script", type="application/ld+json"):
    try:
        data = json.loads(script.string)
        if data.get('@type') == 'Product':
            product_data['name'] = data.get('name')
            product_data['price'] = data['offers']['price']
            product_data['currency'] = data['offers']['priceCurrency']
            product_data['availability'] = data['offers']['availability']
            product_data['url'] = data['offers']['url']
            product_data['rating'] = data.get('aggregateRating', {}).get('ratingValue')
            product_data['reviewCount'] = data.get('aggregateRating', {}).get('reviewCount')
            product_data['image'] = data.get('image')
    except (json.JSONDecodeError, KeyError):
        continue

print(product_data)
