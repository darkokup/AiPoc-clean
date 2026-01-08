"""Application configuration management."""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_environment: str = "development"
    api_title: str = "Clinical Trial Protocol Generator API"
    api_version: str = "0.1.0"
    
    # Database
    database_url: str = "sqlite:///./clinical_trials.db"
    
    # Security
    secret_key: str = "CHANGE-THIS-SECRET-KEY-IN-PRODUCTION"
    access_token_expire_minutes: int = 30
    
    # Model Configuration
    models_path: str = "./models"
    use_local_models: bool = True
    openai_api_key: Optional[str] = None
    
    # Storage
    artifacts_path: str = "./artifacts"
    vector_db_path: str = "./vector_db"
    
    # Logging
    log_level: str = "INFO"
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        protected_namespaces=('settings_',),  # Avoid Pydantic warning
        extra='ignore'  # Ignore extra fields from .env
    )


# Global settings instance
settings = Settings()


# Create necessary directories
os.makedirs(settings.artifacts_path, exist_ok=True)
os.makedirs(settings.vector_db_path, exist_ok=True)
os.makedirs(settings.models_path, exist_ok=True)
