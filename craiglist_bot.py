import telebot
import schedule
import aiohttp
import asyncio
from craiglist_soup import scrape
from config import BOT_TOKEN
import time

bot = telebot.TeleBot(BOT_TOKEN)
processed_posts = set()

async def download_image(url):
    if not url:
        raise ValueError("URL cannot be None or empty")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.read()
    return None

async def send_cars(chat_id):
    cars = await scrape()
    for car in cars:
        car_id = car['url']
        if car_id not in processed_posts:
            car_info = f"""
            Название: {car['title']}
            Цена: {car['price']}
            Местоположение: {car['location']}
            Ссылка: {car['url']}
            """
            try:
                if car['image_path']:
                    image = await download_image(car['image_path'])
                    bot.send_photo(chat_id, image, caption=car_info)
                else:
                    raise ValueError(f"Изображение не найдено для {car['title']}. URL: {car['url']}")
            except Exception as e:
                car_info += f"\nОшибка загрузки изображения: {e}"
                bot.send_message(chat_id, car_info)
            processed_posts.add(car_id)

def start_scheduling(chat_id, interval=600):
    def job():
        print("Updating car listings...")
        asyncio.run(send_cars(chat_id))
    
    job()
    schedule.every(interval).seconds.do(job)

    while True:
        schedule.run_pending()
        time.sleep(3)

@bot.message_handler(commands=['start'])
def start_handler(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Автоматическое обновление каждые 10 минут начато.")
    start_scheduling(chat_id, interval=600)

if __name__ == "__main__":
    bot.polling()
