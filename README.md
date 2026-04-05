# Domesticator — Прототип системы автоматизированного сбора товарных предложений

Прототип системы автоматизированного сбора и актуализации товарных предложений из внешних интернет-источников для e-commerce вертикали. Разработан в рамках выпускной квалификационной работы.

Система позволяет извлекать структурированные данные (цены, наличие, характеристики) с веб-сайтов интернет-магазинов посредством декларативных конфигураций на основе CSS-селекторов без изменения программного кода.

## Технологический стек

- **Python 3.12+**
- **FastAPI** — HTTP-сервер и REST API
- **Playwright + Chromium** — браузерная автоматизация
- **Crawlee** — фреймворк для веб-скрейпинга
- **Pydantic** — валидация данных и схемы API
- **PostgreSQL** — хранение конфигураций (production) / in-memory (development)
- **asyncpg** — асинхронный драйвер PostgreSQL
- **pytest** — тестирование

## Развертывание

### Требования

- **Python** 3.12 или выше
- **Node.js** 18+ (требуется для Playwright)
- **Git**

### Автоматическая установка (рекомендуется)

Скрипт `setup.sh` автоматически установит пакетный менеджер `uv`, зависимости Python, браузер Chromium и создаст файл `.env.local`.

```bash
git clone <repository-url>
cd прототип_v1
bash setup.sh
```

После завершения установки запустите сервер:

```bash
make dev
```

Сервис будет доступен по адресу http://localhost:8000

### Ручная установка

#### macOS

```bash
# 1. Установить Homebrew (если не установлен)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Установить uv (пакетный менеджер Python)
brew install uv

# 3. Клонировать репозиторий
git clone <repository-url>
cd прототип_v1

# 4. Установить зависимости (uv автоматически скачает нужную версию Python)
uv sync --all-extras

# 5. Установить браузер Chromium
uv run playwright install chromium --with-deps

# 6. Создать файл переменных окружения
cp .env.local.example .env.local

# 7. Запустить сервер
APP_ENV=development uv run uvicorn http_api.run:server --reload --host 0.0.0.0 --port 8000
```

#### Linux (Ubuntu/Debian)

```bash
# 1. Установить системные зависимости
sudo apt update
sudo apt install -y curl git

# 2. Установить uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # или ~/.zshrc

# 3. Клонировать репозиторий
git clone <repository-url>
cd прототип_v1

# 4. Установить зависимости
uv sync --all-extras

# 5. Установить Chromium с системными зависимостями
uv run playwright install chromium --with-deps

# 6. Создать файл переменных окружения
cp .env.local.example .env.local

# 7. Запустить сервер
APP_ENV=development uv run uvicorn http_api.run:server --reload --host 0.0.0.0 --port 8000
```

#### Windows

```powershell
# 1. Установить uv
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2. Клонировать репозиторий
git clone <repository-url>
cd прототип_v1

# 3. Установить зависимости
uv sync --all-extras

# 4. Установить Chromium
uv run playwright install chromium

# 5. Создать файл переменных окружения
copy .env.local.example .env.local

# 6. Запустить сервер (или использовать start.bat)
set APP_ENV=development
uv run uvicorn http_api.run:server --reload --host 0.0.0.0 --port 8000
```

Также доступен скрипт `start.bat` для запуска одной командой.

### Docker

```bash
docker build -t domesticator .
docker run -p 8000:8000 -e APP_ENV=development domesticator
```

### Проверка работоспособности

После запуска выполните:

```bash
curl http://localhost:8000/health
```

Ожидаемый ответ:

```json
{"status": "ok", "browser": true, "browser_error": null}
```

## Интерфейсы

| Интерфейс | URL | Описание |
|-----------|-----|----------|
| Веб-интерфейс | http://localhost:8000 | SPA для управления системой |
| Swagger UI | http://localhost:8000/docs | Интерактивная документация API |
| ReDoc | http://localhost:8000/redoc | Документация API (альтернативный формат) |
| OpenAPI | http://localhost:8000/openapi.json | Спецификация OpenAPI 3.1 |

## API

### Служебные эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/` | Веб-интерфейс |
| `GET` | `/ping` | Проверка доступности |
| `GET` | `/health` | Состояние сервиса |
| `GET` | `/v0/status` | Версия и статус |

### Краулинг

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/v0/crawl` | Запуск краулинга целевых URL |

### Управление конфигурациями хостов

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/v0/config/hosts` | Все конфигурации |
| `GET` | `/v0/config/hosts/{hostname}` | Конфигурация хоста |
| `GET` | `/v0/config/hosts/{hostname}/strategies` | Стратегии хоста |
| `POST` | `/v0/config/hosts/{hostname}` | Создать конфигурацию |
| `PUT` | `/v0/config/hosts/{hostname}` | Обновить конфигурацию |
| `DELETE` | `/v0/config/hosts/{hostname}` | Удалить конфигурацию |

### Управление прокси

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/v0/proxies` | Список прокси |
| `POST` | `/v0/proxies/add` | Добавить прокси |
| `DELETE` | `/v0/proxies/{proxy_url}` | Удалить прокси |

## Конфигурация

### Переменные окружения

| Переменная | Значение | Описание |
|------------|----------|----------|
| `APP_ENV` | `development` / `production` | Режим работы |
| `PG_CONNECTION` | `postgresql://...` | Подключение к PostgreSQL (опционально в dev) |
| `PROXY_LIST` | `http://...,socks5://...` | Список прокси через запятую (опционально) |

В режиме `development` без `PG_CONNECTION` система использует in-memory хранилище с начальными конфигурациями из `configs/hosts.json`.

### Предустановленные источники

Прототип включает конфигурации для 10 турецких интернет-магазинов:

1. **trendyol.com** — маркетплейс
2. **amazon.com.tr** — Amazon Турция
3. **hepsiburada.com** — маркетплейс
4. **n11.com** — маркетплейс
5. **idefix.com** — книги и медиа
6. **pazarama.com** — маркетплейс Turkcell
7. **turkcell.com.tr** — оператор связи
8. **akakce.com** — агрегатор цен
9. **pttavm.com** — маркетплейс PTT
10. **kitapyurdu.com** — книжный магазин

## Разработка

### Команды

```bash
make dev          # Запуск с hot reload
make test         # Запуск тестов
make lint         # Проверка кода (ruff)
make format       # Форматирование кода
make health       # Проверка здоровья сервиса
make help         # Все доступные команды
```

### Структура проекта

```
domesticator/
├── http_api/                  # HTTP-сервер
│   ├── routes/                # Обработчики маршрутов
│   │   ├── base.py            # /, /ping, /health
│   │   ├── status.py          # /v0/status
│   │   ├── crawl.py           # /v0/crawl
│   │   ├── hosts.py           # /v0/config/hosts
│   │   └── proxies.py         # /v0/proxies
│   ├── run.py                 # Создание приложения FastAPI
│   ├── serve.py               # Точка входа uvicorn
│   └── routers.py             # Регистрация маршрутов
├── shared/                    # Бизнес-логика
│   ├── browser/               # Модуль краулинга
│   │   ├── bypass/            # Обход защиты
│   │   │   ├── stealth.py     # Stealth-режим браузера
│   │   │   ├── cloudflare.py  # Обход Cloudflare
│   │   │   └── amazon.py      # Обход защиты Amazon
│   │   ├── crawl.py           # Оркестрация краулинга
│   │   ├── crawler.py         # Навигация и извлечение
│   │   └── manager.py         # Управление браузером
│   ├── config/                # Модуль конфигураций
│   │   ├── models.py          # Pydantic-модели
│   │   ├── store.py           # Абстрактный интерфейс
│   │   ├── memory_store.py    # In-memory хранилище
│   │   └── pg_store.py        # PostgreSQL хранилище
│   ├── proxy/                 # Модуль прокси
│   │   ├── manager.py         # Ротация прокси
│   │   ├── store.py           # Абстрактный интерфейс
│   │   ├── memory_store.py    # In-memory хранилище
│   │   └── pg_store.py        # PostgreSQL хранилище
│   └── transform/             # Модуль трансформаций
│       ├── pipeline.py        # Конвейер трансформаций
│       └── transformers/      # 19 функций трансформации
├── configs/
│   └── hosts.json             # Конфигурации 10 источников
├── static/
│   └── index.html             # Веб-интерфейс (SPA)
├── tests/                     # Тесты (pytest)
├── pyproject.toml             # Зависимости и настройки
├── Makefile                   # Команды сборки и запуска
├── Dockerfile                 # Контейнеризация
└── setup.sh                   # Автоматическая установка
```

## Тестирование

```bash
make test
```

Тестовый набор включает 12 модулей: модульные тесты трансформаций, моделей, пайплайна, хранилища конфигураций и менеджера прокси, а также функциональные тесты REST API.

## Лицензия

Прототип разработан в учебных целях в рамках выпускной квалификационной работы.
