# backend/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Установите зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скопируйте исходный код
COPY . .

# Выполните миграции и соберите статику
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

# Запуск приложения и бота
CMD ["sh", "-c", "gunicorn backend.wsgi:application --bind 0.0.0.0:8000 & python main.py"]
