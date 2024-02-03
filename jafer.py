import aiohttp
import asyncio
from bs4 import BeautifulSoup

telegram_bot_token = '6631186152:AAEocsPM0MdY26d-LoDh656KlDl2DPYlKEA'
telegram_channel_username = '@jafferstore'
base_url = 'https://www.jaferbooks.com/'

async def fetch_content(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def scrape_data(html_code):
    soup = BeautifulSoup(html_code, "html.parser")
    books = []
    items = soup.find_all("div", class_="product__style--3")
    for item in items:
        # Extracting Image URL
        image_url = base_url + (item.find("img")["src"] if item.find("img") else "Image URL not found")
        # Extracting Title
        title_tag = item.find("h6")
        title = title_tag.find("a").text.strip() if title_tag and title_tag.find("a") else "Title not found"
        # Extracting Author
        author_tag = item.find("small")
        author = author_tag.text.strip() if author_tag else "Author not found"
        # Extracting Price
        price_tags = item.find_all("ul", class_="prize d-flex")
        price = price_tags[0].find("li").text.strip() if price_tags else "Price not found"
        books.append({
            "Image URL": image_url,
            "Title": title,
            "Author": author,
            "Price": price
        })
    return books

async def send_message_to_telegram(message):
    send_message_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    data = {
        "chat_id": telegram_channel_username,
        "text": message,
        "parse_mode": "HTML"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(send_message_url, data=data) as response:
            if response.status != 200:
                print("Failed to send message to Telegram channel.")

async def main():
    html_code = await fetch_content(base_url)
    books_data = await scrape_data(html_code)
    for book in books_data:
        caption = f"<b>Title:</b> {book['Title']}\n"
        caption += f"<b>Image URL:</b> {book['Image URL']}\n"
        caption += f"<b>Author:</b> {book['Author']}\n"
        caption += f"<b>Price:</b> {book['Price']}"
        await send_message_to_telegram(caption)
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
