from elasticsearch import Elasticsearch

# Подключение к Elasticsearch
es = Elasticsearch("http://localhost:9200")

# Создание индекса
index_name = "test_documents"
es.indices.create(index=index_name, ignore=400)  # Игнорировать ошибку, если индекс уже существует

# Тестовые документы
documents = [
    {
        "id": 1,
        "title": "Путешествие по России",
        "content": "Россия — самая большая страна в мире, с богатой историей и культурой. Путешествие по России может быть увлекательным и познавательным."
    },
    {
        "id": 2,
        "title": "Технологии будущего",
        "content": "Технологии развиваются с невероятной скоростью. Искусственный интеллект и машинное обучение становятся важными аспектами нашей жизни."
    }
]

# Индексация документов
for doc in documents:
    es.index(index=index_name, id=doc["id"], document=doc)

print("Документы успешно проиндексированы.")
