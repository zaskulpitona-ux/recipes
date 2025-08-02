# Telegram Recipes AutoPoster

Автоматический бот для постинга рецептов с Instagram в Telegram-канал.

## Структура

- `recipes.py` — основной скрипт.
- `recipes.csv` — список Instagram-ссылок.
- `requirements.txt` — зависимости.
- `.gitignore` — не добавляет временные файлы в git.
- `Procfile` — команда для запуска (Railway/Heroku).

## Быстрый старт

1. Добавь свои Instagram-ссылки в `recipes.csv`.
2. На Railway в разделе **Variables** добавь:
   - `TG_BOT_TOKEN` — токен Telegram-бота
   - `TG_CHANNEL_ID` — канал (например, `@your_channel` или `-100xxxxxx`)
3. Залей репозиторий на Railway.
4. Railway сам установит зависимости и запустит бот.
