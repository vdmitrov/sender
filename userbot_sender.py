import json
import asyncio
import os
import logging
from telethon import TelegramClient
from datetime import datetime

CONFIG_FILE = "config.json"
CHATS_FILE = "chats.json"
SESSION = "my_userbot"
LOG_FILE = "bot.log"
FORWARD_FILE = "forward.json"

# Настройка логирования
logging.basicConfig(
    filename=LOG_FILE,
    filemode='a',
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.INFO,
    encoding='utf-8'
)

if not os.path.exists(CONFIG_FILE):
    raise FileNotFoundError(f"Нет файла {CONFIG_FILE}")

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    config = json.load(f)

API_ID = config["API_ID"]
API_HASH = config["API_HASH"]

MESSAGE_TEXT = """➿➿➿➿➿➿➿➿➿➿➿
          
        💎💎💎💎💎💎💎💎

➿➿➿➿➿➿➿➿➿➿➿
💎ы ищем ответственных, пряморуких, активных и общительных участников в наши ряды! С желанием развиваться вместе с кланом!
 
💎💎 💎💎💎

➖Розыгрыши 🎫🎫
➖CWL League of Masters ³
➖Raids 1500+
➖CW NoN-Stop

💎💎 💎💎💎

➖🏰, с прямыми руками.
➖Актив в играх кланах.
➖Быть в беседе.

➿➿➿➿➿➿➿➿➿➿➿

        💎💎💎💎💎💎💎💎

➿➿➿➿➿➿➿➿➿➿➿

💎кадемия клана GAMERS.

💎💎 💎💎💎

➖Помощь и поддержка 
➖CWL League Crystal ³
➖Raids 1500+

💎💎 💎💎💎

➖🏠+ тх.
➖Желание развиваться.
➖Актив в играх клана.
➖Быть в беседе.
"""

def load_chats():
    try:
        with open(CHATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Ошибка чтения {CHATS_FILE}: {e}")
        return {}

client = TelegramClient(SESSION, API_ID, API_HASH)

# ---- Новое: отправка фото перед текстом ----
async def send_to_chat(entity, text):
    # Сначала фото
    if os.path.exists(FORWARD_FILE):
        with open(FORWARD_FILE, "r", encoding="utf-8") as f:
            forward = json.load(f)
        if forward.get("enabled") and forward.get("photo_data"):
            photo = forward["photo_data"]
            if photo.get("type") == "photo" and os.path.exists(photo.get("file", "")):
                await client.send_file(entity, photo["file"], caption=photo.get("caption", ""))
                logging.info(f"📷 Фото отправлено в {entity.id}")
                print(f"📷 Фото отправлено в {entity.id}")

    # Потом текст
    if text:
        await client.send_message(entity, text)
        logging.info(f"✅ Текст отправлен в {entity.id}")
        print(f"✅ Текст отправлен в {entity.id}")

async def main_loop():
    await client.start()
    logging.info("Userbot запущен и авторизован.")

    while True:
        chats = load_chats()
        if not chats:
            logging.info("Список чатов пуст, ждем 10 секунд...")
            await asyncio.sleep(10)
            continue

        for url, delay in chats.items():
            try:
                entity = await client.get_entity(url)
                await send_to_chat(entity, MESSAGE_TEXT)  # <-- используем новую функцию
                await asyncio.sleep(delay)
            except Exception as e:
                logging.error(f"Ошибка при отправке в {url}: {e}")

        await asyncio.sleep(5)

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main_loop())
