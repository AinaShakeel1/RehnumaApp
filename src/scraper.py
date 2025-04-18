import requests
from bs4 import BeautifulSoup
import csv
import time
import json

headers = {
    "User-Agent": "Mozilla/5.0"
}

# Start with Fresh Products under Groceries & Pets
base_url = "https://www.naheed.pk"
category_url = "https://www.naheed.pk/groceries-pets/fresh-products"

def get_product_links(category_url):
    product_links = []
    response = requests.get(category_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all product containers
    for a_tag in soup.select("a.product-item-link"):
        link = a_tag['href']
        if link.startswith('/'):
            link = base_url + link
        product_links.append(link)
    
    return list(set(product_links))  # remove duplicates


def get_product_details(product_url):
    response = requests.get(product_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Try to find structured data
    product_data = {
        'name': None,
        'price': None,
        'currency': None,
        'availability': None,
        'url': product_url
    }

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict) and data.get("@type") == "Product":
                product_data['name'] = data.get("name")
                offer = data.get("offers", {})
                product_data['price'] = offer.get("price")
                product_data['currency'] = offer.get("priceCurrency")
                product_data['availability'] = offer.get("availability", "").split('/')[-1]  # get last part
        except json.JSONDecodeError:
            continue
    
    return product_data


def main():
    links = get_product_links(category_url)
    print(f"Found {len(links)} product links.")

    all_data = []
    for idx, url in enumerate(links):
        print(f"[{idx+1}/{len(links)}] Scraping: {url}")
        data = get_product_details(url)
        all_data.append(data)
        time.sleep(1)  # be nice to the server

    # Save to CSV
    with open("naheed_products.csv", "w", newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'price', 'currency', 'availability', 'url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in all_data:
            writer.writerow(item)

    print("✅ Done! Data saved to naheed_products.csv")

if __name__ == "__main__":
    main()
