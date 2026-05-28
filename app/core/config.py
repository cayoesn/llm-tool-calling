from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "LLM Tool Runtime"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # LLM
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "llama3"

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "app"
    POSTGRES_PORT: int = 5432

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Observability
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    PROMETHEUS_PORT: int = 8000
    LOKI_URL: str = "http://localhost:3100/loki/api/v1/push"
    JAEGER_HOST: str = "localhost"
    JAEGER_PORT: int = 6831

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
