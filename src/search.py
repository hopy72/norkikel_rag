import base64
import io
from PIL import Image

from src.indexer import DocumentIndexer
from src.multimodal_inference import MultimodalInference
from src.data_preparation.data_preparer import DocumentDataPreparer


class DocumentSearchService:
    def __init__(
        self, 
        base_data_directory: str = "data/prepared_data/",
        model_name: str = "vidore/colqwen2-v0.1",
        multimodal_model_name: str = 'openbmb/MiniCPM-V-2_6-int4'
    ):
        # Подготовка данных
        self.data_preparer = DocumentDataPreparer(base_data_directory)
        self.dataset = self.data_preparer.prepare_documents()

        # Инициализация индексатора
        self.indexer = DocumentIndexer(
            dataset=self.dataset,
            model_name=model_name
        )

        # Инициализация мультимодальной модели
        self.multimodal_inference = MultimodalInference(
            model_name=multimodal_model_name
        )

    def image_to_base64(self, image: Image.Image) -> str:
        """
        Конвертация изображения в base64 строку
        
        Args:
            image (Image.Image): Изображение для конвертации
        
        Returns:
            str: Base64 строка изображения
        """
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def search_documents(
        self, 
        query: str, 
        top_k: int = 3
    ) -> dict:
        """
        Поиск релевантных документов
        
        Args:
            query (str): Текстовый запрос
            top_k (int): Количество возвращаемых документов
        
        Returns:
            dict: Найденные документы
        """
        try:
            # Поиск релевантных изображений
            relevant_images = self.indexer.search_by_text_and_return_images(
                query, 
                top_k=top_k
        )

        # Подготовка списка документов с base64 изображениями
            documents = []
            images = []
            for idx, image in enumerate(relevant_images):
                doc_info = {
                    "index": idx,
                    "filename": getattr(image, 'filename', 'unknown'),
                    "page_number": getattr(image, 'page_number', None),
                    "width": image.width,
                    "height": image.height,
                    # "image_base64": self.image_to_base64(image)  # Добавляем base64 изображения
                }
                images.append(image)
                documents.append(doc_info)

            return {
                "query": query,
                "documents": documents
            } , images

        except Exception as e:
            print(f"Error in search_documents: {e}")
            raise  # Reraise для получения полного трейсбэка

    def generate_response(
        self, 
        query: str, 
        image: Image.Image
    ) -> str:
        """
        Генерация ответа для конкретного изображения
        
        Args:
            query (str): Текстовый запрос
            image (Image.Image): Изображение для анализа
        
        Returns:
            str: Сгенерированный ответ
        """
        return self.multimodal_inference.generate_response(
            image, 
            query
        )


def main():
    """
    Пример использования DocumentSearchService
    """
    a = 1
    # Инициализация сервиса поиска
    search_service = DocumentSearchService()

    # Примеры запросов
    test_queries = [
        "Какое количество заседаний правительства было в двадцать первом году",
        "Кого привёл Джон Керри на церемонию подписания климатических соглашений",
        "Найди графики и диаграммы"
    ]

    # Тестирование поиска для каждого запроса
    for query in test_queries:
        print(f"Запрос: {query}")
        
        # Сначала ищем документы
        search_result, images = search_service.search_documents(query, top_k=2)
        documents = search_result['documents']
        
        print(f"Найдено документов: {len(documents)}")
        
        # Если есть документы, генерируем ответ для первого
        if documents:
            first_image = images[0]
            response = search_service.generate_response(query, first_image)
            print(f"Ответ модели: {response}")
        else:
            print("Документы не найдены")

if __name__ == "__main__":
    main()
