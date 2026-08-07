"""
Configurações centrais da aplicação, carregadas via variáveis de ambiente (.env).
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    SECRET_KEY: str
    API_PORT: int = 8000
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str

    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_EVIDENCIAS: str = "sigil-evidencias"

    QDRANT_URL: str
    ELASTICSEARCH_URL: str

    KAFKA_BROKER: str
    KAFKA_TOPIC_EVIDENCIAS: str = "evidencias.criadas"
    KAFKA_TOPIC_PIPELINE: str = "pipeline.processamento"
    KAFKA_TOPIC_RETRY: str = "evidencias.retry"
    KAFKA_TOPIC_DEAD_LETTER: str = "evidencias.dead-letter"

    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 30
    MFA_ISSUER_NAME: str = "SIGIL"

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
