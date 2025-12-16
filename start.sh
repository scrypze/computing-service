#!/bin/bash

# Скрипт для запуска Django computing-service

cd "$(dirname "$0")"

# Проверяем, активировано ли виртуальное окружение
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Активируем виртуальное окружение..."
    source venv/bin/activate
fi

# Проверяем, установлены ли зависимости
if ! python -c "import django" 2>/dev/null; then
    echo "Устанавливаем зависимости..."
    pip install -r requirements.txt
fi

# Применяем миграции (если нужно)
echo "Проверяем миграции..."
python manage.py migrate --noinput > /dev/null 2>&1

# Запускаем сервер
echo "Запускаем Django сервер на http://localhost:8000"
python manage.py runserver 0.0.0.0:8000

