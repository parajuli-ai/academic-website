"""
Configuration management for RAG backend
Centralized settings with environment variable support
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with validation"""
    
    # API Configuration
    APP_NAME: str = "Academic RAG API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:4000",
        "http://127.0.0.1:4000",
        "https://tilak-parajuli.github.io",
    ]
    
    # Google AI (Gemini)
    GOOGLE_API_KEY: str
    LLM_MODEL: str = "gemini-1.5-flash"
    EMBED_MODEL: str = "text-embedding-004"
    EMBED_DIMENSION: int = 768  # text-embedding-004 dimension
    
    # Pinecone Vector Database
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str = "us-east-1"
    PINECONE_INDEX_NAME: str = "tilak-academic-site-768"
    
    # Document Processing
    MAX_FILE_SIZE_MB: int = 10
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    SUPPORTED_EXTENSIONS: list[str] = [".pdf", ".txt", ".md", ".docx"]
    
    # RAG Configuration
    TOP_K_RESULTS: int = 5
    SIMILARITY_THRESHOLD: float = 0.3
    MAX_CONTEXT_LENGTH: int = 4000
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 20
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export settings instance
settings = get_settings()

