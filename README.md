# 🧭 Career Compass — IT Career Guidance Platform

**Career Compass** — это веб-приложение для профориентации в IT. Пользователь проходит интерактивный тест из 10 вопросов, а система на основе ответов подбирает наиболее подходящие IT-профессии и строит индивидуальную карьерную карту (roadmap).

Проект разработан в рамках **Кейса №3: «Карьерный компас»** для ИТ-траектории.

---

## 🚀 Быстрый старт (Docker)

```bash
# 1. Клонировать репозиторий
git clone <url-репозитория>
cd centerinvest

# 2. Запустить одной командой
docker compose up -d --build

# 3. Открыть в браузере
#    http://localhost
```

Готово! Фронтенд доступен на `http://localhost`, API — на `http://localhost:8000`.

---

## 🏗 Архитектура проекта

```
┌──────────────┐       ┌──────────────┐      ┌──────────────┐
│   Frontend   │ ───→  │   Backend    │ ──→  │   SQLite     │
│   (nginx)    │  /api  │  (FastAPI)   │      │  (volume)    │
│   :80        │       │  :8000       │      └──────────────┘
└──────────────┘       └──────────────┘
```

| Компонент | Технологии | Описание |
|-----------|-----------|----------|
| **Frontend** | React 18, TypeScript, Vite, CSS Modules | SPA с маршрутизацией, тестом, результатами и roadmap |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy (async), SQLite | REST API с автозагрузкой seed-данных |
| **База данных** | SQLite (aiosqlite) | Файловая БД, сохраняется в Docker volume |
| **Прокси** | nginx (в контейнере frontend) | Раздаёт статику + проксирует /api → backend |

---

## 📋 Возможности

- ✅ **Интерактивный тест** — 10 вопросов с разными типами: single choice, multiple choice, Likert scale, ranking
- ✅ **Подбор профессий** — алгоритм скоринга с учётом рыночного коэффициента
- ✅ **Карьерные карты (roadmap)** — пошаговый план развития для каждой профессии
- ✅ **Регистрация / Авторизация** — JWT-based auth
- ✅ **Отслеживание прогресса** — сохранение результатов теста в профиле
- ✅ **Адаптивный дизайн** — мобильная и десктопная версия
- ✅ **Тёмная тема** — переключение светлой/тёмной темы

---

## 🐳 Контейнеризация

### Backend (`backend/Dockerfile`)

```dockerfile
FROM python:3.11-slim
```

**Особенности:**
- Базовый образ: `python:3.11-slim` (~120 MB)
- Устанавливаются системные зависимости: `curl` (для healthcheck)
- Python-пакеты из `requirements.txt` устанавливаются с `--no-cache-dir`
- Healthcheck настроен на проверку `/health` каждые 15 секунд
- При старте автоматически загружаются seed-данные (профессии, вопросы, roadmaps)
- Запускается через `uvicorn` на порту 8000

**Переменные окружения:**

| Переменная | По умолчанию | Описание |
|-----------|-------------|----------|
| `DATABASE_URL` | `sqlite+aiosqlite:///data/app.db` | Путь к SQLite БД |
| `DEBUG` | `false` | Режим отладки (SQL-логи) |
| `API_V1_PREFIX` | `/api/v1` | Префикс API |
| `APP_NAME` | `CareerCompass` | Название приложения |

### Frontend (`frontend/Dockerfile`)

```dockerfile
# Stage 1: Build (node:20-alpine)
FROM node:20-alpine AS builder

# Stage 2: Serve (nginx:1.27-alpine)
FROM nginx:1.27-alpine
```

**Особенности:**
- **Multi-stage сборка**: сначала собирает статику в `node:20-alpine`, затем раздаёт через `nginx:1.27-alpine`
- **Production build**: `npm run build` (Vite собирает оптимизированный bundle)
- **nginx**: кастомная конфигурация с:
  - Кешированием статики (`/assets/` — 1 год)
  - Проксированием `/api/` → backend
  - SPA fallback (все маршруты → `index.html`)
  - Gzip-сжатием
- **Healthcheck: запрос к корню сайта

**Build-time ARG:**

| ARG | По умолчанию | Описание |
|-----|-------------|----------|
| `VITE_API_URL` | `/api/v1` | Базовый URL API для фронтенда |

### Docker Compose (`docker-compose.yml`)

Оркестрирует два сервиса и один Docker volume:

**Сервисы:**
- `backend` — FastAPI-приложение, порт 8000
- `frontend` — nginx + React SPA, порт 80

**Зависимости:**
- Frontend запускается только после успешного healthcheck бэкенда (`condition: service_healthy`)

**Сеть:**
- Оба контейнера в одной bridge-сети `app-net`

**Volume:**
- `app_data` — persistent storage для SQLite БД (`/app/data`)

---

## 🛠 Команды для разработки

### Docker

```bash
# Запустить в фоне
docker compose up -d

# Пересобрать и запустить
docker compose up -d --build

# Посмотреть логи
docker compose logs -f
docker compose logs -f backend
docker compose logs -f frontend

# Остановить
docker compose down

# Остановить и удалить volume с БД
docker compose down -v

# Зайти в контейнер
docker compose exec backend bash
docker compose exec frontend sh
```

### Без Docker (для разработки)

**Backend:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm ci
npm run dev
```

---

## 🧪 Тестирование

```bash
# Backend tests (pytest)
cd backend
pytest -v

# Frontend tests (vitest)
cd frontend
npm test
```

---

## 🌐 Деплой на production

### Вариант 1: Docker Compose (рекомендуется)

```bash
docker compose up -d --build
```

### Вариант 2: Вручную за reverse proxy (nginx на хосте)

См. конфигурацию nginx в `docs/deploy/it-track.kkeystro.ru.conf` и подробную инструкцию в `docs/`.

```nginx
# Пример базовой конфигурации reverse proxy
server {
    listen 443 ssl;
    server_name your-domain.ru;

    location / {
        root /opt/your-app/frontend;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

---

## 📁 Структура проекта

```
centerinvest/
├── README.md                # ← Этот файл
├── github.md                # Инструкция по работе с GitHub
├── docker-compose.yml       # Оркестрация сервисов
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── app/
│   │   ├── main.py          # FastAPI app + lifespan
│   │   ├── config.py        # Настройки (pydantic-settings)
│   │   ├── database.py      # SQLAlchemy async engine
│   │   ├── api/             # Роутеры (quiz, auth, progress...)
│   │   ├── models/          # SQLAlchemy модели
│   │   ├── schemas/         # Pydantic схемы
│   │   ├── services/        # Бизнес-логика
│   │   └── seed/            # Начальные данные (JSON)
│   ├── alembic/             # Миграции БД
│   └── tests/               # Pytest тесты
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── src/
│   │   ├── pages/           # Страницы приложения
│   │   ├── components/      # UI-компоненты
│   │   ├── api/             # API-клиенты
│   │   ├── context/         # React Contexts
│   │   ├── hooks/           # Custom hooks
│   │   ├── types/           # TypeScript типы
│   │   └── utils/           # Утилиты
│   └── public/
└── .gitignore
```

---

## 🔍 Проверка работоспособности

```bash
# 1. Healthcheck бэкенда
curl http://localhost:8000/health
# → {"status":"ok","app":"CareerCompass"}

# 2. API — начать тест
curl -s -X POST http://localhost/api/v1/quiz/start \
  -H "Content-Type: application/json" -d '{}' | python3 -m json.tool

# 3. Фронтенд отвечает
curl -s -o /dev/null -w "%{http_code}" http://localhost/
# → 200
```

---

## 📄 Лицензия

Copyright © 2026 **IT-Track / Compas team**

Этот проект распространяется под лицензией **GNU General Public License v3.0**.

Вы можете свободно использовать, изменять и распространять этот код в соответствии с условиями GPL v3. Подробнее см. в файле [`LICENCE`](./LICENCE) или на [gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html).
