# Woox Travel Backend (Flask + SMTP)

Запуск локально:

1. Установите Python 3.10+
2. `pip install -r backend/requirements.txt`
3. Установите переменные окружения SMTP (пример PowerShell):
```powershell
$env:SMTP_HOST="smtp.example.com"
$env:SMTP_PORT="587"
$env:SMTP_USER="user@example.com"
$env:SMTP_PASSWORD="pass123"
$env:TO_EMAIL="recipient@example.com"
$env:FROM_EMAIL=""
$env:SMTP_USE_TLS="true"
$env:PORT="5000"
```
4. Запуск: `python backend/app.py`

Эндпоинты:
- GET `http://localhost:5000/health`
- POST `http://localhost:5000/api/reservations`

Тело POST (JSON):
```json
{
  "Name": "Иван Иванов",
  "Number": "+7 900 000-00-00",
  "Guests": "3",
  "date": "2025-12-20",
  "Destination": "Швейцария, Лозанна"
}
```
