import os
from pydantic_settings import BaseSettings
from typing import Optional, Any
from pydantic import model_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "AII2046SMS"
    
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    
    FEISHU_APP_ID: Optional[str] = None
    FEISHU_APP_SECRET: Optional[str] = None
    FEISHU_ENCRYPT_KEY: Optional[str] = None
    FEISHU_VERIFICATION_TOKEN: Optional[str] = None

    # Monitor Settings
    MONITOR_HEARTBEAT_TIMEOUT: int = 180  # 3 minutes in seconds    
    MONITOR_CHECK_INTERVAL: int = 180     # 3 minutes in seconds    
    MONITOR_ALERT_RECIPIENT_ID: Optional[str] = None
    MONITOR_ALERT_RECIPIENT_TYPE: str = "feishu_chat" 
    MONITOR_ALERT_AT_USER_ID: Optional[str] = None # "all" for everyone, or user_open_id
    
    @model_validator(mode='before')
    @classmethod
    def load_secrets(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Mapping of field name to secret file name
            # Docker secrets are typically mounted in /run/secrets/
            secret_map = {
                "POSTGRES_USER": "postgres_user",
                "POSTGRES_PASSWORD": "postgres_passwd",
                "POSTGRES_DB": "postgres_db",
            }
            
            secrets_dir = "/run/secrets"
            
            for field, secret_name in secret_map.items():
                secret_path = os.path.join(secrets_dir, secret_name)
                if os.path.exists(secret_path):
                    try:
                        with open(secret_path, "r") as f:
                            # Prioritize secret content over env var
                            value = f.read().strip()
                            if value:
                                data[field] = value
                    except Exception as e:
                        # Log warning if needed, but don't crash
                        pass
        return data

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def CELERY_BROKER_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
