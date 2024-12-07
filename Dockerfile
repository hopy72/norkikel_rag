# Используем образ Python 3.12.3 slim
FROM python:3.12.3-slim-bookworm

# Устанавливаем рабочую директорию
WORKDIR /app

# Сначала копируем файл requirements.txt для использования кэша Docker
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install -r requirements.txt

# Открываем необходимые порты
EXPOSE 8000

# Команда для запуска приложения (настройте при необходимости)
CMD ["python", "src/main.py"]