# Используем официальный образ Python
FROM python:3.9-slim

# Рабочая директория
WORKDIR /app

# Копируем зависимости и исходный код
COPY requirements.txt .
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт для веб-сервера
EXPOSE 5000

# Запускаем оба процесса через launch.pyw
CMD ["python", "launch.pyw"]