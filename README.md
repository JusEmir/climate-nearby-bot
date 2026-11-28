# Climate Nearby Bot

Telegram-бот и небольшой веб-сервис об экологических советах и локальных проблемах, связанных с окружающей средой и изменением климата.

## Возможности

- `/start`, `/help`, `/tips` — команды Telegram-бота.
- `/map` — ссылка на веб-карту сообщений.
- API советов: `GET /api/tips` и фильтр `GET /api/tips?category=жара`.
- API сообщений: `GET /api/problems` (GeoJSON) и `POST /api/problems`.
- Страница карты `/map` с просмотром и отправкой сообщений.
- Сообщения хранятся в SQLite (`data/climate_nearby.sqlite3` по умолчанию).

Сообщения на карте помечены как **не проверенные**. Это учебный MVP, не официальный сервис экстренного реагирования; не публикуйте персональные данные. В продакшене добавьте модерацию, защиту от спама и HTTPS.

## Установка и запуск

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env       # Windows: copy .env.example .env
```

Заполните `.env`:

```text
TELEGRAM_BOT_TOKEN=ваш_токен
PUBLIC_BASE_URL=http://127.0.0.1:8000
# DATABASE_PATH=data/climate_nearby.sqlite3
```

Запустите API и карту в одном терминале:

```bash
uvicorn api:app --reload
```

Откройте http://127.0.0.1:8000/map (документация API: http://127.0.0.1:8000/docs).

Чтобы запустить бота, в другом терминале выполните:

```bash
python bot.py
```

Для команды `/map` укажите `PUBLIC_BASE_URL` как публичный адрес сервера, доступный пользователям Telegram. Локальный адрес `127.0.0.1` виден только на вашем компьютере.

## API

Пример отправки сообщения:

```bash
curl -X POST http://127.0.0.1:8000/api/problems \\
  -H 'Content-Type: application/json' \\
  -d '{"category":"мусор","description":"Стихийная свалка у дороги","latitude":55.75,"longitude":37.62}'
```

Допустимые категории: `мусор`, `загрязнение воздуха`, `жара`, `другое`. Координаты проверяются по диапазону широты и долготы; описание ограничено 500 символами.

## Структура

```text
├── advice.py       # локальная база советов
├── api.py          # FastAPI и SQLite API
├── bot.py          # Telegram-бот
├── map.html        # веб-карта и форма сообщения
├── requirements.txt
└── .env.example
```
