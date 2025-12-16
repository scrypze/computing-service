# Инструкция по тестированию

## Шаг 1: Запуск Django-сервиса

1. Перейдите в директорию computing-service:
```bash
cd /Users/erikray/Developer/computing-service
```

2. Создайте виртуальное окружение (если еще не создано):
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Запустите сервер:
```bash
python manage.py runserver 0.0.0.0:8000
```

Сервер должен запуститься на порту 8000.

## Шаг 2: Запуск основного Go-сервиса

1. В новом терминале перейдите в директорию основного сервиса:
```bash
cd /Users/erikray/Developer/develop-internet-applications
```

2. Убедитесь, что конфигурация правильная (config/config.toml):
- `ComputingServiceURL = "http://localhost:8000"`
- `ComputingServiceToken = "12345678"`

3. Запустите сервер:
```bash
go run cmd/exocalc/main.go
```

Или используйте Makefile, если он есть.

## Шаг 3: Тестирование через API

### 3.1. Проверка работы Django-сервиса

Проверьте, что Django-сервис отвечает:
```bash
curl -X POST http://localhost:8000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "selected_stars_id": 1,
    "star_id": 1,
    "star_data": {
      "luminosity": "1.0",
      "radius": "1.0",
      "temperature": "5778",
      "mass": "1.0",
      "metallicity": "0.0"
    }
  }'
```

Ожидаемый ответ: `{"status": "accepted", "message": "Calculation started", ...}`

### 3.2. Тестирование полного цикла

1. **Авторизуйтесь в основном сервисе** (получите JWT токен):
```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login": "your_login", "password": "your_password"}'
```

2. **Создайте заявку** (если нужно):
```bash
curl -X POST http://localhost:8080/api/selected-stars \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

3. **Добавьте звезды в заявку**:
```bash
curl -X POST http://localhost:8080/api/selected-stars/add-star/STAR_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

4. **Сформируйте заявку**:
```bash
curl -X PUT http://localhost:8080/api/selected-stars/SELECTED_STARS_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"date": "2025-01-15", "scientist": "Test Scientist"}'
```

5. **Завершите заявку модератором** (это вызовет асинхронный расчет):
```bash
curl -X PUT http://localhost:8080/api/selected-stars/SELECTED_STARS_ID/moderate \
  -H "Authorization: Bearer MODERATOR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "complete", "moderator_id": "MODERATOR_UUID"}'
```

6. **Подождите 5-10 секунд** и проверьте результаты:
```bash
curl -X GET http://localhost:8080/api/selected-stars/SELECTED_STARS_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

7. **Проверьте список заявок** (должно быть поле `calculated_count`):
```bash
curl -X GET http://localhost:8080/api/selected-stars \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Шаг 4: Проверка логов

Проверьте логи обоих сервисов:

**Django-сервис** должен показывать:
- Принятие запроса на расчет
- Отправку результата в основной сервис

**Go-сервис** должен показывать:
- Вызов computing service при завершении заявки
- Прием результатов от computing service

## Возможные проблемы

1. **Django-сервис не запускается**: проверьте, что все зависимости установлены
2. **Ошибка подключения**: убедитесь, что оба сервиса запущены и порты правильные
3. **Ошибка токена**: проверьте, что токены совпадают в обоих сервисах (12345678)
4. **Результаты не обновляются**: проверьте логи Django-сервиса, возможно ошибка при отправке результата

