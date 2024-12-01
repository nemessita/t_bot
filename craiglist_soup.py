# craiglist_soup.py
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from config import url_add

URL = url_add
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"
}

async def fetch(session, url):
    async with session.get(url, headers=HEADERS) as response:
        return await response.text()

async def scrape():
    cars = []
    async with aiohttp.ClientSession() as session:
        page_content = await fetch(session, URL)
        soup = BeautifulSoup(page_content, 'html.parser')

        result = soup.find('ol', class_="cl-static-search-results")
        car_elements = result.find_all('li', class_='cl-static-search-result')

        tasks = [fetch_car_details(session, car_elem) for car_elem in car_elements[:20]]
        cars = await asyncio.gather(*tasks)
    return cars

async def fetch_car_details(session, car_elem):
    title_elem = car_elem.find('div', class_='title')
    price_elem = car_elem.find('div', class_='price')
    location_elem = car_elem.find('div', class_='location')
    url_elem = car_elem.find('a', href=True)['href']

    car_soup_content = await fetch(session, url_elem)
    car_soup = BeautifulSoup(car_soup_content, 'html.parser')
    img = car_soup.find('a', class_='thumb')
    image_path = img['href'] if img else None

    return {
        'title': title_elem.get_text(strip=True) if title_elem else 'N/A',
        'price': price_elem.get_text(strip=True) if price_elem else 'N/A',
        'location': location_elem.get_text(strip=True) if location_elem else 'N/A',
        'url': url_elem,
        'image_path': image_path
    }

if __name__ == "__main__":
    cars = asyncio.run(scrape())
    for car in cars:
        print(car)
