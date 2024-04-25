from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import sqlite3
import time, random

def setup_driver():
    options = Options()
    options.headless = True  # Run in headless mode
    driver = webdriver.Chrome(options=options)
    return driver

def fetch_page(url, driver):
    try:
        driver.get(url)
        time.sleep(random.uniform(8, 15))  # Random sleep time between 8 and 15 seconds
        data = driver.page_source
        return data
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_html(data):
    return BeautifulSoup(data, 'html.parser')

def extract_data_landwatch(soup):
    placards = soup.find_all('div', id=lambda x: x and x.startswith('placard-container'))
    return [{
        'price': placard.find_all('span')[0].text.strip() if placard else "Not found",
        'size': placard.find_all('span')[3].text.strip() if len(placard.find_all('span')) > 3 else "Not found",
        'address': placard.find('p', class_="af8d6").text.strip() if placard.find('p', class_="af8d6") else "Not found"
    } for placard in placards]

def extract_data_landsearch(soup):
    placards = soup.find_all('article', class_="preview $property")
    data = []
    for placard in placards:
        title_div = placard.find('div', class_="preview__title")
        if title_div:
            full_text = title_div.get_text(strip=True)
            size = title_div.find('span', class_="preview__size").text.strip() if title_div.find('span', class_="preview__size") else "Not found"
            
            # Extract the price by replacing the size text with nothing, leaving only the price
            price = full_text.replace(size, '') if size != "Not found" else "Not found"
        else:
            price = "Not found"
            size = "Not found"
        
        location_div = placard.find('div', class_="preview__location $pinpoint")
        address = location_div.text.strip() if location_div else "Not found"

        data.append({'price': price, 'size': size, 'address': address})
    return data

def setup_database():
    conn = sqlite3.connect('lodb.db')
    c = conn.cursor()
    # Drop the existing table if it exists, then create a new table
    c.execute('''DROP TABLE IF EXISTS listings''')
    c.execute('''CREATE TABLE listings (price TEXT, size TEXT, address TEXT)''')
    return conn, c

def store_data(data, cursor):
    for item in data:
        # Only insert data if the price contains a dollar sign
        if '$' in item['price']:
            cursor.execute('''INSERT INTO listings (price, size, address) VALUES (?, ?, ?)''', (item['price'], item['size'], item['address']))
        else:
            print(f"Skipping entry with invalid price: {item}")

def main():
    driver = setup_driver()
    landwatch_url = 'https://www.landwatch.com/north-carolina-land-for-sale/sort-newest/page-'
    conn, cursor = setup_database()

    for page in range(1, 6):  # Loop through the first 5 pages
        url = f"{landwatch_url}{page}"
        print(f"Fetching data from {url}")
        data = fetch_page(url, driver)
        soup = parse_html(data)
        extracted_data = extract_data_landwatch(soup)
        store_data(extracted_data, cursor)


    landsearch_url = 'https://www.landsearch.com/properties/north-carolina/filter/sort=-newest,structure=0/p'

    for page in range(1, 3):  # Loop through the first 5 pages
        url = f"{landsearch_url}{page}"
        print(f"Fetching data from {url}")
        data = fetch_page(url, driver)
        soup = parse_html(data)
        extracted_data = extract_data_landsearch(soup)
        print(extracted_data)
        store_data(extracted_data, cursor)

    conn.commit()
    conn.close()
    driver.quit()
    print("Data extraction and storage complete.")

if __name__ == '__main__':
    main()