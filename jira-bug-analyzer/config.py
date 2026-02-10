"""
Application configuration settings
"""
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List, Literal


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Jira Bug Analyzer"
    DEBUG: bool = True
    
    # Jira 认证信息
    JIRA_EMAIL: str
    JIRA_TOKEN: str
    JIRA_DOMAIN: str = "https://softwareone.atlassian.net"
    
    # Azure OpenAI 配置
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_DEPLOYMENT_NAME: str
    AZURE_OPENAI_API_VERSION: str
    
    # 模型配置
    MODEL_TEMPERATURE: float = 0.7
    
    # LLM生成阈值配置
    LLM_RETRY_TIMES: int = 3
    LLM_TIMEOUT_SECONDS: int = 60
    
    class Config:
        env_file = str(Path(__file__).resolve().parent / ".env")
        env_file_encoding = "utf-8"


settings = Settings()
