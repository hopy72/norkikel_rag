"""
Модуль для индексации и поиска документов с использованием Qdrant и ColQwen2.
"""

import yaml
import torch
from typing import List, Dict, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models
from tqdm import tqdm

from colpali_engine.models import ColQwen2, ColQwen2Processor
from src.data_preparation.data_preparer import DocumentDataPreparer  # Импорт вашего data preparer
from PIL import Image


class DocumentIndexer:
    def __init__(
        self,
        dataset: List[Image.Image] = None,
        model_name: str = "vidore/colqwen2-v0.1", 
        qdrant_host: str = "localhost", 
        collection_name: str = "nornikel_prod",
    ):
        """
        Инициализация индексатора документов
        """
        # Инициализация модели и процессора
        self.model = ColQwen2.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            device_map="cuda:0"
        )
        self.processor = ColQwen2Processor.from_pretrained(model_name)
        
        # Инициализация Qdrant клиента
        self.qdrant_client = QdrantClient(host=qdrant_host)
        self.collection_name = collection_name
        
        # Параметры векторизации
        self.vector_size = None
        
        # Инициализация DocumentDataPreparer
        self.dataset = dataset

    def create_collection(
        self, 
        vector_size: Optional[int] = None, 
        distance: models.Distance = models.Distance.COSINE
    ):
        """
        Создание коллекции в Qdrant
        """
        if vector_size is None:
            # Получаем размер вектора из первого изображения
            sample_image = self.dataset[0]
            with torch.no_grad():
                sample_batch = self.processor.process_images([sample_image]).to(self.model.device)
                sample_embedding = self.model(**sample_batch)
                vector_size = sample_embedding.shape[2]

        self.vector_size = vector_size

        vector_params = models.VectorParams(
            size=vector_size,
            distance=distance,
            multivector_config=models.MultiVectorConfig(
                comparator=models.MultiVectorComparator.MAX_SIM
            ),
            quantization_config=models.ScalarQuantization(
                scalar=models.ScalarQuantizationConfig(
                    type=models.ScalarType.INT8,
                    quantile=0.99,
                    always_ram=True,
                ),
            ),
        )
        
        self.qdrant_client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=vector_params,
            on_disk_payload=True
        )

    def index_documents(
        self, 
        batch_size: int = 16, 
        metadata: Dict[str, str] = {"source": "document_archive"}
    ):
        """
        Индексация документов
        """
        # Получение подготовленных изображений

        # Создание коллекции, если она еще не создана
        if self.vector_size is None:
            self.create_collection()
        
        # Индексация с прогресс-баром
        with tqdm(total=len(self.dataset), desc="Indexing Documents") as pbar:
            for i in range(0, 3, batch_size):
                batch = self.dataset[i : i + batch_size]
                
                # Генерация эмбеддингов
                with torch.no_grad():
                    batch_images = self.processor.process_images(batch).to(self.model.device)
                    image_embeddings = self.model(**batch_images)
                
                # Подготовка точек для Qdrant
                points = []
                for j, embedding in enumerate(image_embeddings):
                    multivector = embedding.cpu().float().numpy().tolist()
                    points.append(
                        models.PointStruct(
                            id=i + j,
                            vector=multivector,
                            payload={
                                **metadata,
                                "filename": batch[j].filename,
                                "page_number": getattr(batch[j], 'page_number', None),
                                "text": getattr(batch[j], 'text', None)  # Добавляем текст из изображения
                            }
                        )
                    )
                
                # Загрузка точек в Qdrant
                self.qdrant_client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                
                pbar.update(len(batch))

        print("Indexing complete!")

    def search_documents(
        self, 
        query_text: str, 
        top_k: int = 5
    ) -> List[Dict]:
        """
        Поиск документов по текстовому запросу
        """
        # Генерация эмбеддинга запроса
        with torch.no_grad():
            batch_query = self.processor.process_queries([query_text]).to(self.model.device)
            query_embedding = self.model(**batch_query)
        
        # Конвертация эмбеддинга
        multivector_query = query_embedding[0].cpu().float().numpy().tolist()
        
        # Поиск в Qdrant
        search_result = self.qdrant_client.query_points(
            collection_name=self.collection_name, 
            query=multivector_query, 
            limit=top_k
        )
        
        return search_result

    def search_by_text_and_return_images(self, query_text, top_k=5):
        results = self.search_documents(query_text, top_k)
        row_ids = [r.id for r in results.points]
        return [self.dataset[i] for i in row_ids]

    def index_new_documents(
            self,
            new_dataset: List[Image.Image],
            batch_size: int = 16,
            metadata: Dict[str, str] = {"source": "document_archive"},
        ):
            """
            Индексация новых документов, добавленных в набор данных
            """
            # Получение ID уже проиндексированных документов
            indexed_ids = [i for i in range(self.qdrant_client.count(self.collection_name))]
            # Фильтрация новых документов
            new_documents = [doc for i, doc in enumerate(new_dataset) if i not in indexed_ids]

            # Индексация новых документов с прогресс-баром
            with tqdm(total=len(new_documents), desc="Indexing New Documents") as pbar:
                for i in range(0, len(new_documents), batch_size):
                    if i not in indexed_ids:
                        batch = new_documents[i : i + batch_size]

                        # Генерация эмбеддингов
                        with torch.no_grad():
                            batch_images = self.processor.process_images(batch).to(self.model.device)
                            image_embeddings = self.model(**batch_images)
                        
                        # Подготовка точек для Qdrant
                        points = []
                        for j, embedding in enumerate(image_embeddings):
                            multivector = embedding.cpu().float().numpy().tolist()
                            points.append(
                                models.PointStruct(
                                    id=i + j,
                                    vector=multivector,
                                    payload={
                                        **metadata,
                                        "filename": batch[j].filename,
                                        "page_number": getattr(batch[j], 'page_number', None),
                                        "text": getattr(batch[j], 'text', None)  # Добавляем текст из изображения
                                    }
                                )
                            )
                            
                            # Загрузка точек в Qdrant
                            self.qdrant_client.upsert(
                                collection_name=self.collection_name,
                                points=points
                            )
                            
                            pbar.update(len(batch))

            print("Индексация новых документов завершена!")


def main():
    """
    Пример использования
    """
    data_preparer = DocumentDataPreparer("data/prepared_data/")
    dataset = data_preparer.prepare_documents()

    # Создание индексатора с параметрами из конфигурации
    indexer = DocumentIndexer(
        dataset=dataset,
        model_name='vidore/colqwen2-v0.1',
        qdrant_host='localhost',
        collection_name='document_collection'
    )

    # Создание коллекции
    # indexer.create_collection()

    # Индексация документов
    # indexer.index_documents(
    #     batch_size=3,
    #     metadata={"source": "document_archive"},
    # )

    # Пример поиска
    query = "Джон Керри климатические соглашения"
    results = indexer.search_by_text_and_return_images(query, top_k=5)

    for result in results:
        print(result)

if __name__ == "__main__":
    main()