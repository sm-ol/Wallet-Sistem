Программа для управления кошельками и пользователями на FastAPI, 
SQLAlchemy и Pydantic. Расчеты ведутся в типе Decimal

СТРУКТУРА ПРОЕКТА
* main.py          — Точка входа приложения и подключение роутеров
* database.py      — Настройка подключения к MySQL (драйвер pymysql)
* models.py        — ORM-модели таблиц SQLAlchemy (users и wallets)
* schemas.py       — Схемы Pydantic для валидации JSON
* wallet.py        — Финансовая бизнес-логика на чистом Python
* test_wallet.py   — Модульные тесты для логики классов wallet
* test_api.py      — Интеграционные тесты для эндпоинтов FastAPI
* routers/users.py   — Роутер для создания пользователей
* routers/wallets.py — Роутер для операций: создание, пополнение, списание


ИНСТРУКЦИЯ ПО ЗАПУСКУ

1. Установите библиотеки в виртуальном окружении:
   pip install fastapi uvicorn sqlalchemy pymysql pydantic pytest httpx2

2. Запустите сервер разработки:
   uvicorn main:app --reload

3. Ссылки на интерактивную документацию (в браузере):
   * Swagger UI: http://127.0.0
   * ReDoc:      http://127.0.0

4. Запустите автоматические тесты:
   pytest test_api.py -v
   pytest test_wallet.py -v


