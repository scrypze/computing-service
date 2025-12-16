# Computing Service

Асинхронный сервис вычислений на Django для расчета экзопланет.

## Описание

Сервис выполняет асинхронные расчеты зоны обитаемости и вероятного количества планет для звезд. Расчет выполняется с задержкой 5-10 секунд и результат отправляется обратно в основной сервис.

## Установка

1. Создайте виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate  # для MacOS/Linux
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

4. Настройте переменные окружения в `.env`:
- `MAIN_SERVICE_URL` - URL основного сервиса (по умолчанию: http://localhost:8080)
- `MAIN_SERVICE_TOKEN` - токен для авторизации (8 байт, по умолчанию: 12345678)

## Запуск

### Способ 1: Используя скрипт (рекомендуется)

```bash
./start.sh
```

### Способ 2: Вручную

1. Активируйте виртуальное окружение:
```bash
source venv/bin/activate
```

2. Запустите сервер:
```bash
python manage.py runserver 0.0.0.0:8000
```

Сервер запустится на `http://localhost:8000`

### Проверка работы

После запуска проверьте, что сервис работает:
```bash
curl http://localhost:8000/api/calculate
```

Или откройте в браузере: `http://localhost:8000/api/calculate` (должна быть ошибка метода, но это нормально - значит сервер работает)

## API

### POST /api/calculate

Запускает асинхронный расчет для звезды в заявке.

**Запрос:**
```json
{
  "selected_stars_id": 1,
  "star_id": 5,
  "star_data": {
    "luminosity": "1.0",
    "radius": "1.0",
    "temperature": "5778",
    "mass": "1.0",
    "metallicity": "0.0"
  }
}
```

**Ответ:**
```json
{
  "status": "accepted",
  "message": "Calculation started",
  "selected_stars_id": 1,
  "star_id": 5
}
```

Расчет выполняется асинхронно с задержкой 5-10 секунд, после чего результат отправляется в основной сервис через HTTP POST запрос на `/api/calculate-exoplanets/update-result`.

