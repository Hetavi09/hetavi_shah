import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd

def scrape_amazon(search_query, output_file):
    search_query = search_query.replace(" ", "+")
    url = f"https://www.amazon.com/s?k={search_query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve data from Amazon. HTTP Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, "html.parser")
    products = []
    for item in soup.select(".s-main-slot .s-result-item"):
        title = item.select_one("h2 .a-link-normal")
        title_text = title.get_text(strip=True) if title else None

        price_whole = item.select_one(".a-price-whole")
        price_fraction = item.select_one(".a-price-fraction")
        price = f"{price_whole.get_text(strip=True)}.{price_fraction.get_text(strip=True)}" if price_whole and price_fraction else None

        link = title["href"] if title else None
        link = f"https://www.amazon.com{link}" if link else None

        if title_text and price and link:
            products.append({"name": title_text, "price": price, "link": link})

    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["name", "price", "link"])
        writer.writeheader()
        writer.writerows(products)

    print(f"Amazon data saved to {output_file}")

def scrape_books_to_scrape(base_url, output_file):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}

    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Product Name", "Price($)", "Reviews"])

        page_url = base_url

        while page_url:
            response = requests.get(page_url, headers=headers)
            if response.status_code != 200:
                print(f"Failed to fetch page: {page_url}")
                break

            soup = BeautifulSoup(response.content, 'html.parser')
            books = soup.find_all("article", class_="product_pod")

            for book in books:
                name = book.h3.a["title"]
                price = book.find("p", class_="price_color").text
                rating_class = book.find("p", class_="star-rating")["class"]
                rating = rating_class[1] if len(rating_class) > 1 else "No rating"

                writer.writerow([name, price, rating])

            next_page = soup.find("li", class_="next")
            if next_page:
                next_page_link = next_page.a["href"]
                page_url = base_url.rsplit('/', 1)[0] + '/' + next_page_link
            else:
                page_url = None

    print(f"Books data saved to {output_file}")

def scrape_ebay(search_query, output_file):
    search_query = search_query.replace(" ", "+")
    search_url = f'https://www.ebay.com/sch/i.html?_nkw={search_query}'
    response = requests.get(search_url)

    if response.status_code != 200:
        print(f"Failed to retrieve data from eBay. HTTP Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    product_containers = soup.find_all('div', class_='s-item__info')

    product_data = []
    for container in product_containers:
        title = container.find('h3', class_='s-item__title')
        title_text = title.text.strip() if title else "N/A"

        price = container.find('span', class_='s-item__price')
        price_text = price.text.strip() if price else "N/A"

        link = container.find('a', class_='s-item__link')
        link_href = link['href'] if link else "N/A"

        product_data.append({
            'Product Name': title_text,
            'Price': price_text,
            'Link': link_href
        })

    df = pd.DataFrame(product_data)
    df.to_csv(output_file, index=False)
    print(f"eBay data saved to {output_file}")

if __name__ == "__main__":
    print("Select the website to scrape:")
    print("1. Amazon")
    print("2. Books to Scrape")
    print("3. eBay")

    choice = input("Enter your choice (1/2/3): ")

    if choice == "1":
        search_term = input("Enter the product to search on Amazon: ")
        output_file = input("Enter the name of the CSV file to save the results (e.g., amazon_products.csv): ")
        scrape_amazon(search_term, output_file)
    elif choice == "2":
        BASE_URL = "http://books.toscrape.com/catalogue/page-1.html"
        output_file = input("Enter the name of the CSV file to save the results (e.g., books_to_scrape.csv): ")
        scrape_books_to_scrape(BASE_URL, output_file)
    elif choice == "3":
        search_term = input("Enter the product to search on eBay: ")
        output_file = input("Enter the name of the CSV file to save the results (e.g., ebay_products.csv): ")
        scrape_ebay(search_term, output_file)
    else:
        print("Invalid choice. Exiting.")