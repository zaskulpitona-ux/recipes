import os
import csv
import asyncio
from aiogram import Bot
from yt_dlp import YoutubeDL

# --- 1. Настройки ---
TOKEN = os.getenv("TG_BOT_TOKEN")
CHANNEL_ID = os.getenv("TG_CHANNEL_ID")
RECIPES_CSV = "recipes.csv"
POSTED_CSV = "posted.csv"
DOWNLOAD_DIR = "downloads"

# --- 2. Утилиты для работы с файлами и данными ---

def read_urls_from_csv(csv_path):
    """Читает ссылки из файла рецептов"""
    urls = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            url = row.get('url')
            if url:
                urls.append(url.strip())
    return urls

def read_posted_urls(posted_csv):
    """Читает уже опубликованные ссылки, чтобы не постить повторно"""
    if not os.path.exists(posted_csv):
        return set()
    with open(posted_csv, newline='', encoding='utf-8') as csvfile:
        return set(row['url'] for row in csv.DictReader(csvfile))

def save_posted_url(posted_csv, url):
    """Сохраняет опубликованную ссылку"""
    file_exists = os.path.exists(posted_csv)
    with open(posted_csv, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['url'])
        if not file_exists:
            writer.writeheader()
        writer.writerow({'url': url})

# --- 3. Загрузка видео и описания из Instagram ---

def download_instagram_video_and_caption(url, output_dir=DOWNLOAD_DIR):
    """Скачивает видео и парсит описание/заголовок из Instagram"""
    os.makedirs(output_dir, exist_ok=True)
    ydl_opts = {
        'outtmpl': f'{output_dir}/%(id)s.%(ext)s',
        'format': 'mp4/bestvideo+bestaudio/best',
        'quiet': True,
        'skip_download': False,
        'force_overwrites': True,
        'writeinfojson': True,  # сохраняет метаданные
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        description = info.get('description') or ""
        title = info.get('title') or ""
        video_path = ydl.prepare_filename(info)
        return video_path, description.strip(), title.strip()

# --- 4. Отправка поста в Telegram-канал ---

async def send_recipe(bot, channel_id, text, video_path):
    """Отправляет видео и текст в канал"""
    if not text:
        text = "Рецепт без описания"
    if len(text) > 1024:
        text = text[:1020] + "..."
    with open(video_path, "rb") as video:
        await bot.send_video(chat_id=channel_id, video=video, caption=text)

# --- 5. Основная логика ---

async def main():
    bot = Bot(token=TOKEN)
    urls = read_urls_from_csv(RECIPES_CSV)
    posted = read_posted_urls(POSTED_CSV)
    for url in urls:
        if url in posted:
            print(f"Уже опубликовано: {url}")
            continue
        print(f"Обрабатываем: {url}")
        try:
            video_path, description, title = download_instagram_video_and_caption(url)
            # Формируем подпись к посту
            if title and description and title not in description:
                text = f"{title}\n\n{description}"
            else:
                text = description or title or "Рецепт"
            await send_recipe(bot, CHANNEL_ID, text, video_path)
            save_posted_url(POSTED_CSV, url)
            print(f"Опубликовано: {url}")
            await asyncio.sleep(5)  # пауза между постами, чтобы не словить лимиты
        except Exception as e:
            print(f"Ошибка при обработке {url}: {e}")
    await bot.session.close()

# --- 6. Точка входа ---

if __name__ == "__main__":
    asyncio.run(main())
