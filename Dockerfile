# Используем образ Python 3.12.3 slim
FROM python:3.12.3-slim-bookworm

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем переменные окружения для Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Сначала копируем файл requirements.txt для использования кэша Docker
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код приложения
COPY . .

# Создаем пользователя без прав root для безопасности
RUN addgroup --system appuser && \
    adduser --system --ingroup appuser appuser

# Меняем владельца директории приложения
RUN chown -R appuser:appuser /app

# Переключаемся на пользователя без прав root
USER appuser

# Открываем необходимые порты
EXPOSE 8000

# Команда для запуска приложения (настройте при необходимости)
CMD ["python", "main.py"]