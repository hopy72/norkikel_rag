import os  # Импорт os для работы с файлами

import fitz  # PyMuPDF для работы с PDF
from PIL import Image  # Импорт PIL для работы с изображениями
import io  # Импорт io для работы с байтовыми потоками

from docx2pdf import convert
from tqdm.notebook import tqdm  # Импорт прогресс-бара для Jupyter


def pdf_to_pil_images(pdf_path, output_directory):
    # Открываем PDF файл
    pdf_document = fitz.open(pdf_path)

    for page_number in tqdm(range(len(pdf_document))):
        # Получаем страницу
        page = pdf_document.load_page(page_number)

        # Рендерим страницу в изображение (pixmap)
        pix = page.get_pixmap()

        # Конвертируем pixmap в PIL изображение
        img = Image.open(io.BytesIO(pix.tobytes()))

        # Сохраняем изображение в выходную директорию
        image_filename = os.path.join(output_directory, f"{os.path.basename(pdf_path)}_page_{page_number + 1}.png")
        img.save(image_filename)

    # Закрываем PDF документ
    pdf_document.close()

def convert_all_files(directory, output_directory):
    # Создаем выходную директорию, если она не существует
    os.makedirs(output_directory, exist_ok=True)

    for filename in tqdm(os.listdir(directory)):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(directory, filename)
            pdf_to_pil_images(pdf_path, output_directory)

def convert_docx_to_pdf(input_directory):
    """
    Конвертирует все .docx файлы в указанной директории в PDF формат
    
    Args:
        input_directory (str): Путь к директории с .docx файлами
    """
    # Проходим по всем файлам в директории
    for filename in os.listdir(input_directory):
        # Проверяем расширение файла
        if filename.endswith('.docx'):
            # Формируем полный путь к файлу
            input_path = os.path.join(input_directory, filename)
            # Конвертируем .docx в PDF в ту же директорию
            convert(input_path, input_directory)


if __name__ == "__main__":
    # Конвертируем .docx файлы в PDF
    convert_docx_to_pdf("../data/raw_files")

    # Конвертируем все PDF файлы в изображения
    convert_all_files("../data/raw_files/", "../data/prepared_data/")
