import gradio as gr
import numpy as np
from PIL import Image
import fitz
import os
import shutil
from datetime import datetime
from search import *


chat_history = []

# Определяем базовый путь проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Создаем путь для загрузки файлов
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "raw_files")

# Создаем директорию, если она не существует
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

def load_local_image(file_path):
    """
    Загружает изображение из локального файла, если оно существует
    
    Args:
        file_path (str): Путь к файлу изображения
        
    Returns:
        PIL.Image или None: Объект изображения или None, если файл не найден
    """
    try:
        if os.path.exists(file_path):
            return Image.open(file_path)
        return None
    except Exception as e:
        print(f"Ошибка при загрузке изображения {file_path}: {e}")
        return None


def generate_response(input_text, pdf_file):
    try:
        pdf_text = ""
        saved_pdf_path = None
        
        if pdf_file is not None:
            # Создаем уникальное имя файла с временной меткой
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"document_{timestamp}.pdf"
            saved_pdf_path = os.path.join(UPLOAD_DIR, filename)
            
            # Копируем загруженный файл в нашу директорию
            shutil.copy2(pdf_file.name, saved_pdf_path)
            
            # Читаем содержимое PDF
            doc = fitz.open(saved_pdf_path)
            for page in doc:
                pdf_text += page.get_text()
            doc.close()
            
            print(f"PDF сохранен по пути: {saved_pdf_path}")
        print(pdf_text)



        search_service = DocumentSearchService()
        print(f"Запрос: {input_text}")
        
        # Сначала ищем документы
        search_result, images = search_service.search_documents(input_text, top_k=2)
        documents = search_result['documents']
        print(f"Найдено документов: {len(documents)}")
        
        # Если есть документы, генерируем ответ для первого
        if documents:
            first_image = images[0]
            response = search_service.generate_response(input_text, first_image)
            print(f"Ответ модели: {response}")
        else:
            print("Документы не найдены")

        # Добавляем запрос и ответ в историю
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chat_history.append({
            "timestamp": timestamp,
            "query": input_text,
            "response": response
        })
        
        return response, images[0] if images else None, images[1] if len(images) > 1 else None, documents
    except Exception as e:
        error_image = np.zeros((200, 200, 3), dtype=np.uint8)
        return f"Произошла ошибка: {str(e)}", error_image, error_image, []
        

with gr.Blocks() as demo:
    gr.Markdown("### Демонстрационное приложение")
    
    with gr.Row():
        input_text = gr.Textbox(label="Введите ваш запрос", 
                              placeholder="Например: Как работает GPT?")
        pdf_input = gr.File(label="Загрузите PDF файл (необязательно)", 
                          file_types=[".pdf"])
    
    with gr.Row():
        output_text = gr.Textbox(label="Текстовый ответ", interactive=False)


    with gr.Row():
        history_box = gr.Dataframe(
            headers=["Время", "Запрос", "Ответ"],
            label="История запросов",
            interactive=False
        )
    
    def update_and_show_response(input_text, pdf_file):
        response, img1, img2, documents = generate_response(input_text, pdf_file)
    
        # Получаем информацию о документах
        if documents and len(documents) > 0:
            doc1 = documents[0]
            filename1_val = doc1['filename'].split('.pdf')[0] + '.pdf'
            page1_val = str(doc1['page_number'])
        else:
            filename1_val = ""
            page1_val = ""
        
        if documents and len(documents) > 1:
            doc2 = documents[1]
            filename2_val = doc2['filename'].split('.pdf')[0] + '.pdf'
            page2_val = str(doc2['page_number'])
        else:
            filename2_val = ""
            page2_val = ""
    
        # Формируем данные для таблицы истории
        history_data = [[h["timestamp"], h["query"], h["response"]] for h in chat_history]
    
        return [
        response, 
        img1, img2,
        filename1_val, page1_val,
        filename2_val, page2_val,
        history_data
    ]
    
    with gr.Row():
        with gr.Column():
            image_output1 = gr.Image(label="Изображение 1")
            # Добавляем информацию под первым изображением
            with gr.Row():
                filename1 = gr.Textbox(label="Файл", interactive=False, scale=2)
                page1 = gr.Textbox(label="Страница", interactive=False, scale=1)
        
        with gr.Column():
            image_output2 = gr.Image(label="Изображение 2")
            # Добавляем информацию под вторым изображением
            with gr.Row():
                filename2 = gr.Textbox(label="Файл", interactive=False, scale=2)
                page2 = gr.Textbox(label="Страница", interactive=False, scale=1)
    
    button = gr.Button("Сгенерировать ответ")
    button.click(
        update_and_show_response,
        inputs=[input_text, pdf_input],
        outputs=[
            output_text, 
            image_output1, image_output2,
            filename1, page1,
            filename2, page2,
            history_box
        ]
    )

demo.launch(share=True)