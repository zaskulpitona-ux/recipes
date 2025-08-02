import os
import csv
import asyncio
from aiogram import Bot
from yt_dlp import YoutubeDL

# Railway автоматически подставляет переменные окружения!
TOKEN = os.getenv("TG_BOT_TOKEN")
CHANNEL_ID = os.getenv("TG_CHANNEL_ID")
RECIPES_CSV = "recipes.csv"
POSTED_CSV = "posted.csv"
DOWNLOAD_DIR = "downloads"

def download_instagram_video_and_caption(url, output_dir=DOWNLOAD_DIR):
    os.makedirs(output_dir, exist_ok=True)
    ydl_opts = {
        'outtmpl': f'{output_dir}/%(id)s.%(ext)s',
        'format': 'mp4/bestvideo+bestaudio/best',
        'quiet': True,
        'skip_download': False,
        'force_overwrites': True,
        'writeinfojson': True,  # сохраняем метаданные
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        description = info.get('description') or ""
        title = info.get('title') or ""
        video_path = ydl.prepare_filename(info)
        return video_path, description.strip(), title.strip()

def read_urls_from_csv(csv_path):
    urls = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            url = row.get('url')
            if url:
                urls.append(url.strip())
    return urls

def read_posted_urls(posted_csv):
    if not os.path.exists(posted_csv):
        return set()
    with open(posted_csv, newline='', encoding='utf-8') as csvfile:
        return set(row['url'] for row in csv.DictReader(csvfile))

def save_posted_url(posted_csv, url):
    file_exists = os.path.exists(posted_csv)
    with open(posted_csv, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['url'])
        if not file_exists:
            writer.writeheader()
        writer.writerow({'url': url})

async def send_recipe(bot, channel_id, text, video_path):
    if not text:
        text = "Рецепт без описания"
    if len(text) > 1024:
        text = text[:1020] + "..."
    with open(video_path, "rb") as video:
        await bot.send_video(chat_id=channel_id, video=video, caption=text)

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
            if title and description and title not in description:
                text = f"{title}\n\n{description}"
            else:
                text = description or title or "Рецепт"
            await send_recipe(bot, CHANNEL_ID, text, video_path)
            save_posted_url(POSTED_CSV, url)
            print(f"Опубликовано: {url}")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Ошибка при обработке {url}: {e}")
    await bot.session.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
