# content_pack_bot

Telegram-бот для продажи AI-контент-пакетов на 30 дней. Создан для экспертов, коучей, психологов, маркетологов и малого бизнеса.

---

## Что умеет бот

1. Проводит пользователя через 7-шаговый мастер (платформа → ниша → продукт → аудитория → цель → тон → длина).
2. Генерирует **бесплатное демо**: 3 темы, 1 полный пост, 1 промпт для визуала.
3. После оплаты (или тестового разблокирования) генерирует **полный пакет**:
   - 30 тем по дням
   - 30 хуков и 30 идей CTA
   - 15 полных постов
   - 15 промптов для ИИ-изображений
   - Контент-календарь
4. Отдаёт готовые файлы `.md` и `.txt` для скачивания.

Модель генерации: **MiniMax M2.5** через Anthropic-совместимый API.

---

## Структура проекта

```
content_pack_bot/
├── src/
│   ├── main.py                  # Точка входа
│   ├── config.py                # Настройки из .env
│   ├── bot/
│   │   ├── handlers/
│   │   │   ├── menu.py          # Главное меню, /start, помощь
│   │   │   └── wizard.py        # FSM мастер + генерация
│   │   ├── keyboards/
│   │   │   ├── main_menu.py     # Reply-клавиатура
│   │   │   └── wizard.py        # Inline-клавиатуры мастера
│   │   ├── middlewares/
│   │   │   └── db_middleware.py # Инъекция репозиториев
│   │   ├── states.py            # FSM-состояния
│   │   └── texts.py             # Все тексты интерфейса
│   ├── core/
│   │   ├── enums.py             # Перечисления
│   │   ├── schemas.py           # Pydantic-модели
│   │   ├── prompt_builder.py    # Сборщики промптов
│   │   ├── content_service.py   # Логика 2-этапной генерации
│   │   ├── formatter.py         # Форматирование в HTML/MD/TXT
│   │   └── validators.py        # JSON-парсинг с авторемонтом
│   ├── integrations/
│   │   ├── minimax_client.py    # Клиент MiniMax (Anthropic SDK)
│   │   └── payments.py          # Провайдеры платежей
│   ├── storage/
│   │   ├── db.py                # Инициализация SQLite
│   │   └── repo.py              # Репозитории (User, Session, Pack, Payment)
│   ├── utils/
│   │   ├── logging.py
│   │   ├── text.py
│   │   └── files.py
│   └── tests/
│       ├── test_config.py
│       ├── test_schemas.py
│       ├── test_validators.py
│       ├── test_formatter.py
│       ├── test_payments.py
│       └── test_repo.py
├── data/
│   └── packs/{user_id}/         # Готовые файлы пользователей
├── conftest.py
├── pytest.ini
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Быстрый старт

### 1. Клонируй и установи зависимости

```bash
git clone <repo>
cd content_pack_bot
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Настрой переменные окружения

```bash
cp .env.example .env
```

Открой `.env` и заполни:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic
ANTHROPIC_API_KEY=your_minimax_api_key
MINIMAX_MODEL=MiniMax-M2.5
APP_ENV=dev
ENABLE_TEST_UNLOCK=true
FULL_PLAN_PRICE_RUB=299
DATABASE_PATH=./data/bot.db
ADMIN_USER_ID=         # твой Telegram user_id (опционально)
```

### 3. Запусти бота

```bash
python -m src.main
```

Бот запускается через long polling — никаких вебхуков и серверов не нужно.

---

## Переменные окружения

| Переменная | Описание | По умолчанию |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Токен от @BotFather | **обязательно** |
| `ANTHROPIC_API_KEY` | API-ключ MiniMax | **обязательно** |
| `ANTHROPIC_BASE_URL` | Базовый URL API | `https://api.minimax.io/anthropic` |
| `MINIMAX_MODEL` | Модель для генерации | `MiniMax-M2.5` |
| `APP_ENV` | Окружение (`dev` / `production`) | `dev` |
| `ENABLE_TEST_UNLOCK` | Включить тестовый доступ без оплаты | `true` |
| `FULL_PLAN_PRICE_RUB` | Цена полного пакета в рублях | `299` |
| `DATABASE_PATH` | Путь к SQLite-базе | `./data/bot.db` |
| `ADMIN_USER_ID` | Telegram ID администратора | — |

---

## Как работает тестовый доступ

Если `ENABLE_TEST_UNLOCK=true` или `APP_ENV=dev`, в боте появляется кнопка **🧪 Тестовый доступ**. При нажатии вместо реального платежа срабатывает `DummyPaymentProvider` — он мгновенно возвращает успех и запускает генерацию полного пакета.

Это позволяет тестировать весь флоу без реального платёжного шлюза.

В `production`-режиме (`APP_ENV=production`, `ENABLE_TEST_UNLOCK=false`) тестовая кнопка скрывается. Для подключения реальных платежей — см. раздел ниже.

---

## Где хранятся файлы

Готовые контент-пакеты сохраняются в:

```
data/packs/{telegram_user_id}/content_pack.md
data/packs/{telegram_user_id}/content_pack.txt
```

Папка создаётся автоматически. Каждая новая генерация перезаписывает файлы пользователя. Если нужна история — добавь timestamp в имя файла в `content_service.py`.

---

## Как подключить реальный платёжный провайдер

1. Открой `src/integrations/payments.py`.
2. Найди класс `TelegramPaymentProvider` — в нём уже есть scaffold.
3. Реализуй метод `create_payment`: отправь инвойс через `bot.send_invoice(...)`.
4. Добавь хэндлеры `pre_checkout_query` и `successful_payment` в `src/bot/handlers/`.
5. В функции `get_payment_provider()` замени `DummyPaymentProvider()` на `TelegramPaymentProvider(token=...)`.
6. Установи `APP_ENV=production` и `ENABLE_TEST_UNLOCK=false` в `.env`.

---

## Как переиспользовать бизнес-логику в веб-приложении

Вся генерация вынесена в `src/core/` и не зависит от Telegram:

```python
from src.core.content_service import ContentService
from src.core.schemas import UserAnswers
from src.core.enums import Platform, Goal, Tone, PostLength
from src.integrations.minimax_client import MinimaxClient
from src.config import load_config
from pathlib import Path

config = load_config()
client = MinimaxClient(config)
service = ContentService(client, packs_dir=Path("data/packs"))

answers = UserAnswers(
    platform=Platform.TELEGRAM,
    niche="маркетинг",
    product="консультация",
    audience="малый бизнес",
    goal=Goal.SALES,
    tone=Tone.SIMPLE,
    length=PostLength.MEDIUM,
)

# Демо
demo = await service.generate_demo(answers)

# Полный пакет
pack, md_path, txt_path = await service.generate_full_pack(answers, user_id=1)
```

Подключи эти сервисы в FastAPI / Django — интерфейс не изменится.

---

## Запуск тестов

```bash
pytest
```

Тесты используют временную in-memory SQLite базу и не требуют реального API-ключа.

---

## Что нажать первым в Telegram

1. Найди бота по имени, нажми **Start**.
2. Нажми **🧪 Пример** — увидишь пример поста из реального пакета.
3. Нажми **✨ Создать пакет** — запустится 7-шаговый мастер.
4. После мастера нажми **✅ Сгенерировать демо**.
5. После демо нажми **🧪 Тестовый доступ** — получишь полный пакет бесплатно.
6. Скачай `.md` или `.txt` кнопками в результате.

---

## Пример поста из пакета

**Ниша:** психология отношений | **Платформа:** Telegram | **Тон:** живой

> Молчание — не знак согласия. Иногда это последнее, что человек делает перед уходом.
>
> Три признака, что клиент уходит, и как это остановить:
> — перестал задавать вопросы
> — отвечает коротко и с задержкой
> — перестал делиться деталями
>
> Что я делаю иначе теперь: звоню сам через 2 недели, спрашиваю конкретно, фиксирую письменно.
>
> **Когда ты последний раз выходил на связь первым?**

🖼 Промпт: `Minimalist illustration of an empty chair at a table, soft natural light, muted tones, metaphor for absence, editorial photography style`
