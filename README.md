
# Инструкция по запуску проекта

Для запуска проекта необходимо выполнить следующие шаги:

Python 3.12.3

1. Разаврхивировать qdrant_storage.rar в корень проекта

2. Создать и активировать виртуальное окружение:
   ```
   python -m venv myenv
   myenv\Scripts\activate
   ```

2. Установить PyTorch:
   ```
   pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu124
   ```

3. Установить зависимости:
   ```
   pip install -r requirements.txt
   ```

3. Запустить Docker образ Qdrant:
   ```
   docker run -p 6333:6333 -p 6334:6334 -v "%cd%/qdrant_storage:/qdrant/storage" qdrant/qdrant
   ```

4. Запустить файл `test_MVP.py`:
   ```
   python -m src.test_MVP
   ```

После выполнения этих шагов проект будет готов к работе.