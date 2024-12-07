from dataclasses import dataclass

@dataclass
class EnvironmentConfig:
    """
    Конфигурация окружения сервиса.

    Attributes:
        mode (str): Режим работы сервиса (development, staging, production)
        debug (bool): Флаг режима отладки
    """
    mode: str = "production"  # development, staging, production
    debug: bool = False

@dataclass 
class LoggingConfig:
    """
    Конфигурация логирования.

    Attributes:
        level (str): Уровень логирования (INFO, DEBUG, ERROR и т.д.)
        format (str): Формат сообщений лога
        file_path (str): Путь к файлу лога
    """
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "logs/service.log"

@dataclass
class QdrantConfig:
    """
    Конфигурация Qdrant.

    Attributes:
        host (str): Хост сервера Qdrant
        port (int): Порт сервера Qdrant
        collection_name (str): Название коллекции
    """
    host: str = "localhost"
    port: int = 6333
    collection_name: str = "nornikel_prod"

@dataclass
class DatabaseConfig:
    """
    Конфигурация базы данных.

    Attributes:
        qdrant (QdrantConfig): Конфигурация Qdrant
    """
    qdrant: QdrantConfig = QdrantConfig()

@dataclass
class ModelConfig:
    """
    Конфигурация модели.

    Attributes:
        name (str): Название модели
        provider (str): Провайдер модели
        device (str): Устройство для вычислений
        dtype (str): Тип данных для вычислений
    """
    name: str = "vidore/colqwen2-v0.1"
    provider: str = "colpali_engine"
    device: str = "cuda:0"
    dtype: str = "bfloat16"

@dataclass
class IndexingMetadata:
    """
    Метаданные для индексации.

    Attributes:
        source (str): Источник документов
    """
    source: str = "document_archive"

@dataclass
class IndexingConfig:
    """
    Конфигурация индексации.

    Attributes:
        data_directory (str): Директория с данными
        batch_size (int): Размер батча для обработки
        metadata (IndexingMetadata): Метаданные индексации
    """
    data_directory: str = "data/prepared_data/"
    batch_size: int = 3
    metadata: IndexingMetadata = IndexingMetadata()

@dataclass
class SearchConfig:
    """
    Конфигурация поиска.

    Attributes:
        default_top_k (int): Количество результатов по умолчанию
        max_top_k (int): Максимальное количество результатов
    """
    default_top_k: int = 5
    max_top_k: int = 20

@dataclass
class SecurityConfig:
    """
    Конфигурация безопасности.

    Attributes:
        rate_limit (int): Ограничение количества запросов в минуту
        timeout (int): Таймаут запроса в секундах
    """
    rate_limit: int = 100  # запросов в минуту
    timeout: int = 30  # секунд

@dataclass
class PrometheusConfig:
    """
    Конфигурация Prometheus.

    Attributes:
        port (int): Порт для метрик Prometheus
    """
    port: int = 8000

@dataclass
class MonitoringConfig:
    """
    Конфигурация мониторинга.

    Attributes:
        enabled (bool): Флаг включения мониторинга
        prometheus (PrometheusConfig): Конфигурация Prometheus
    """
    enabled: bool = True
    prometheus: PrometheusConfig = PrometheusConfig()

@dataclass
class CacheConfig:
    """
    Конфигурация кэширования.

    Attributes:
        enabled (bool): Флаг включения кэширования
        type (str): Тип кэша (redis)
        host (str): Хост сервера кэша
        port (int): Порт сервера кэша
        ttl (int): Время жизни кэша в секундах
    """
    enabled: bool = True
    type: str = "redis"
    host: str = "localhost"
    port: int = 6379
    ttl: int = 3600  # секунд

@dataclass
class ServiceConfig:
    """
    Основная конфигурация сервиса.

    Attributes:
        environment (EnvironmentConfig): Конфигурация окружения
        logging (LoggingConfig): Конфигурация логирования
        database (DatabaseConfig): Конфигурация базы данных
        model (ModelConfig): Конфигурация модели
        indexing (IndexingConfig): Конфигурация индексации
        search (SearchConfig): Конфигурация поиска
        security (SecurityConfig): Конфигурация безопасности
        monitoring (MonitoringConfig): Конфигурация мониторинга
        cache (CacheConfig): Конфигурация кэширования
    """
    environment: EnvironmentConfig = EnvironmentConfig()
    logging: LoggingConfig = LoggingConfig()
    database: DatabaseConfig = DatabaseConfig()
    model: ModelConfig = ModelConfig()
    indexing: IndexingConfig = IndexingConfig()
    search: SearchConfig = SearchConfig()
    security: SecurityConfig = SecurityConfig()
    monitoring: MonitoringConfig = MonitoringConfig()
    cache: CacheConfig = CacheConfig()
