import os
import asyncio
from aiogram import Bot, Dispatcher, types
from yt_dlp import YoutubeDL
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TG_BOT_TOKEN")
CHANNEL_ID = os.getenv("TG_CHANNEL_ID")
POSTED_TXT = "posted_urls.txt"
DOWNLOAD_DIR = "downloads"

# --- Вспомогательные функции ---

def is_instagram_url(text):
    return "instagram.com" in text

def save_posted_url(url):
    with open(POSTED_TXT, "a", encoding="utf-8") as f:
        f.write(url.strip() + "\n")

def is_url_posted(url):
    if not os.path.exists(POSTED_TXT):
        return False
    with open(POSTED_TXT, "r", encoding="utf-8") as f:
        return url.strip() in [line.strip() for line in f.readlines()]

def download_instagram_video_and_caption(url, output_dir=DOWNLOAD_DIR):
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

# --- Основная логика бота ---

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(lambda msg: is_instagram_url(msg.text))
async def handle_instagram_recipe(message: types.Message):
    url = message.text.strip()
    if is_url_posted(url):
        await message.reply("Этот рецепт уже был опубликован.")
        return
    await message.reply("Скачиваю видео и публикую рецепт...")
    try:
        video_path, description, title = download_instagram_video_and_caption(url)
        # Формируем подпись
        if title and description and title not in description:
            text = f"{title}\n\n{description}"
        else:
            text = description or title or "Рецепт"
        # Отправляем в канал
        with open(video_path, "rb") as video:
            await bot.send_video(chat_id=CHANNEL_ID, video=video, caption=text)
        save_posted_url(url)
        await message.reply("Готово! Рецепт опубликован в канале.")
    except Exception as e:
        await message.reply(f"Произошла ошибка при обработке: {e}")

@dp.message()
async def help_msg(message: types.Message):
    await message.reply(
        "Пришли ссылку на рецепт в Instagram (Reels или пост) — видео и описание будут опубликованы в канале автоматически."
    )

async def main():
    print("Bot started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
