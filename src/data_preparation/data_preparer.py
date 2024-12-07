import os
from typing import List, Dict, Optional
from PIL import Image


class DocumentDataPreparer:
    """
    Класс для подготовки документов к индексации.
    
    Основные функции:
    - Чтение изображений из директории
    - Фильтрация и предобработка изображений
    - Добавление метаданных к изображениям
    """

    def __init__(self, base_directory: str):
        """
        Инициализация препаратора данных
        
        Args:
            base_directory (str): Базовая директория с документами
        """
        self.base_directory = base_directory

    def read_png_files(
        self, 
        subdirectory: Optional[str] = None, 
        filter_conditions: Optional[Dict[str, str]] = None
    ) -> List[Image.Image]:
        """
        Чтение PNG файлов с возможностью фильтрации

        Args:
            subdirectory (str, optional): Поддиректория внутри base_directory
            filter_conditions (dict, optional): Условия фильтрации файлов
        
        Returns:
            List[Image.Image]: Список изображений с метаданными
        """
        # Определение полного пути к директории
        directory = os.path.join(self.base_directory, subdirectory) if subdirectory else self.base_directory

        # Список для хранения изображений
        png_images = []

        # Перебор файлов в директории
        for filename in os.listdir(directory):
            if filename.endswith('.png'):
                image_path = os.path.join(directory, filename)
                
                # Открытие изображения
                img = Image.open(image_path)
                
                # Добавление метаданных
                img.filename = filename
                
                # Извлечение номера страницы, если возможно
                if '_page_' in filename:
                    try:
                        page_num = int(filename.split('_page_')[-1].split('.')[0])
                        img.page_number = page_num
                    except (IndexError, ValueError):
                        img.page_number = None
                
                # Применение фильтрации, если указаны условия
                if filter_conditions:
                    skip_image = False
                    for key, value in filter_conditions.items():
                        # Проверка соответствия метаданных условиям
                        if key == 'min_width' and img.width < value:
                            skip_image = True
                            break
                        elif key == 'max_width' and img.width > value:
                            skip_image = True
                            break
                        elif key == 'min_height' and img.height < value:
                            skip_image = True
                            break
                        elif key == 'max_height' and img.height > value:
                            skip_image = True
                            break
                        elif key == 'page_number' and img.page_number != value:
                            skip_image = True
                            break
                    
                    if skip_image:
                        img.close()
                        continue

                png_images.append(img)

        return png_images

    def preprocess_images(
        self, 
        images: List[Image.Image], 
        target_size: Optional[tuple] = None,
        convert_mode: Optional[str] = None,
    ) -> List[Image.Image]:
        """
        Предобработка изображений
        
        Args:
            images (List[Image.Image]): Список изображений
            target_size (tuple, optional): Целевой размер изображений
            convert_mode (str, optional): Режим конвертации цвета

        Returns:
            List[Image.Image]: Предобработанные изображения
        """
        for i, img in enumerate(images):
            # Конвертация цветового режима
            if convert_mode:
                images[i] = img.convert(convert_mode)

            # Изменение размера, если указан target_size
            if target_size:
                images[i] = images[i].resize(target_size, Image.LANCZOS)

        a = 1
        return images

    def prepare_documents(
        self, 
        subdirectory: Optional[str] = None,
        filter_conditions: Optional[Dict[str, str]] = None,
        target_size: Optional[tuple] = None
    ) -> List[Image.Image]:
        """
        Полный цикл подготовки документов
        
        Args:
            subdirectory (str, optional): Поддиректория для поиска
            filter_conditions (dict, optional): Условия фильтрации
            target_size (tuple, optional): Целевой размер изображений

        Returns:
            List[Image.Image]: Подготовленные изображения
        """
        # Чтение изображений
        images = self.read_png_files(
            subdirectory=subdirectory, 
            filter_conditions=filter_conditions
        )

        # Предобработка изображений
        processed_images = self.preprocess_images(
            images, 
            target_size=target_size
        )

        return processed_images

# Пример использования
def main():
    # Пример инициализации и использования
    data_preparer = DocumentDataPreparer("data/prepared_data/")

    # Пример фильтрации и подготовки
    documents = data_preparer.prepare_documents(
        # filter_conditions={
        #     'min_width': 800,
        #     'max_width': 2000,
        #     'min_height': 600
        # },
        # target_size=(1024, 1024)
    )

    print(f"Prepared {len(documents)} documents")

if __name__ == "__main__":
    main()
