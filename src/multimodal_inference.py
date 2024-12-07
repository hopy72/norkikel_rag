"""
Модуль для мультимодального вывода с использованием предобученной модели.
Позволяет генерировать текстовые ответы на основе изображений и текстовых запросов.
"""

import torch
from PIL import Image
from transformers import AutoModel, AutoTokenizer


class MultimodalInference:
    def __init__(
        self, 
        model_name: str = 'openbmb/MiniCPM-V-2_6-int4', 
        device: str = 'cuda' if torch.cuda.is_available() else 'cpu'
    ):
        """
        Инициализация модели мультимодального вывода
        
        Args:
            model_name (str): Идентификатор модели из Hugging Face
            device (str): Устройство для запуска модели
        """
        # Загрузка модели и токенизатора
        self.model = AutoModel.from_pretrained(
            model_name, 
            trust_remote_code=True
        ).to(device)
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name, 
            trust_remote_code=True
        )
        
        self.model.eval()
        self.device = device

    def generate_response(
        self, 
        image: Image.Image, 
        query: str, 
        max_length: int = 2048
    ) -> str:
        """
        Генерация ответа на основе изображения и запроса
        
        Args:
            image (Image.Image): Входное изображение
            query (str): Текстовый запрос об изображении
            max_length (int): Максимальная длина генерируемого ответа
        
        Returns:
            str: Ответ модели на запрос
        """
        try:
            # Подготовка сообщений в формате, ожидаемом моделью
            msgs = [{'role': 'user', 'content': [image, query]}]

            # Генерация ответа
            with torch.no_grad():
                response = self.model.chat(
                    image=image, 
                    msgs=msgs, 
                    tokenizer=self.tokenizer,
                    max_length=max_length
                )

            return response

        except Exception as e:
            print(f"Ошибка при выводе: {e}")
            return "Извините, не удалось обработать изображение и запрос."


def main():
    """
    Пример использования MultimodalInference
    """
    # Инициализация движка вывода
    inference_engine = MultimodalInference()

    # Загрузка примера изображения
    example_image = Image.open('data/prepared_data/2_5282802846297776741.pdf_page_1.png')
    
    # Пример запроса
    query = "Что происходит на этом изображении?"

    # Генерация ответа
    response = inference_engine.generate_response(example_image, query)
    
    print("Запрос:", query)
    print("Ответ:", response)

if __name__ == "__main__":
    main()
