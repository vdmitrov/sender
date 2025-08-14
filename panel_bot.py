from telebot import TeleBot, types
import json
import os
import logging

CONFIG_FILE = "config.json"
CHATS_FILE = "chats.json"
LOG_FILE = "bot.log"
FORWARD_FILE = "forward.json"
IMAGES_DIR = "images"
os.makedirs(IMAGES_DIR, exist_ok=True)

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

BOT_TOKEN = config["BOT_TOKEN"]
bot = TeleBot(BOT_TOKEN)

def load_chats():
    try:
        with open(CHATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Ошибка загрузки чатов: {e}")
        return {}

def save_chats(data):
    try:
        with open(CHATS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"Список чатов обновлён: {list(data.keys())}")
    except Exception as e:
        logging.error(f"Ошибка сохранения чатов: {e}")

@bot.message_handler(commands=['start'])
def start(message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("➕ Добавить чат", "📋 Список чатов")
    kb.add("🗑 Удалить чат")
    bot.send_message(message.chat.id, "📢 Панель рассылки активирована!", reply_markup=kb)
    logging.info(f"/start от {message.from_user.id} ({message.from_user.username})")

@bot.message_handler(func=lambda m: m.text == "📋 Список чатов")
def list_chats(message):
    chats = load_chats()
    if not chats:
        bot.send_message(message.chat.id, "📭 Список пуст")
        logging.info(f"Список чатов запрошен {message.from_user.id}, но он пуст")
        return
    text = "📋 Список чатов:\n"
    for url, delay in chats.items():
        text += f"{url} — задержка {delay} сек.\n"
    bot.send_message(message.chat.id, text)
    logging.info(f"Список чатов отправлен {message.from_user.id}")

@bot.message_handler(func=lambda m: m.text == "➕ Добавить чат")
def add_chat_prompt(message):
    bot.send_message(message.chat.id, "Отправь в формате:\nссылка_на_чат задержка_в_сек")
    logging.info(f"Пользователь {message.from_user.id} начал добавление чата")

@bot.message_handler(func=lambda m: m.text == "🗑 Удалить чат")
def remove_chat_prompt(message):
    bot.send_message(message.chat.id, "Отправь ссылку на чат для удаления")
    logging.info(f"Пользователь {message.from_user.id} начал удаление чата")

@bot.message_handler(content_types=['text'])
def process_text(message):
    parts = message.text.split()
    if len(parts) == 2 and parts[0].startswith("http"):
        url, delay = parts
        try:
            delay = int(delay)
        except ValueError:
            bot.send_message(message.chat.id, "❌ Задержка должна быть числом")
            logging.warning(f"Пользователь {message.from_user.id} ввёл некорректную задержку: {delay}")
            return
        chats = load_chats()
        chats[url] = delay
        save_chats(chats)
        bot.send_message(message.chat.id, f"✅ Чат {url} добавлен с задержкой {delay} сек.")
        logging.info(f"Добавлен чат {url} с задержкой {delay} сек. пользователем {message.from_user.id}")
    elif message.text.startswith("http"):
        url = message.text.strip()
        chats = load_chats()
        if url in chats:
            del chats[url]
            save_chats(chats)
            bot.send_message(message.chat.id, f"🗑 Чат {url} удалён")
            logging.info(f"Удалён чат {url} пользователем {message.from_user.id}")
        else:
            bot.send_message(message.chat.id, "❌ Чат не найден")
            logging.warning(f"Пользователь {message.from_user.id} попытался удалить несуществующий чат {url}")

# ---- Новое: обработка фото ----
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_path = os.path.join(IMAGES_DIR, "logo.jpg")
    with open(file_path, "wb") as f:
        f.write(downloaded_file)

    # Обновляем forward.json
    forward_data = {
        "use_text": True,
        "use_custom": True,
        "use_forward": False,
        "forward_data": {},
        "enabled": True,
        "photo_data": {
            "type": "photo",
            "file": file_path,
            "caption": message.caption if message.caption else ""
        }
    }

    with open(FORWARD_FILE, "w", encoding="utf-8") as f:
        json.dump(forward_data, f, ensure_ascii=False, indent=2)

    bot.send_message(message.chat.id, "✅ Фото сохранено для рассылки")
    logging.info(f"Фото сохранено {file_path} пользователем {message.from_user.id}")

bot.polling(none_stop=True)
