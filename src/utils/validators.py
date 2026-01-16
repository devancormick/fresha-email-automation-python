from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from src.utils.logger import logger

class SMTPConfig(BaseModel):
    host: str = Field(..., min_length=1)
    port: int = Field(..., ge=1, le=65535)
    user: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    from_email: EmailStr
    from_name: str = Field(..., min_length=1)
    
    @validator('port')
    def validate_port(cls, v):
        if v not in [25, 465, 587, 993, 995]:
            logger.warning(f'Unusual SMTP port: {v}')
        return v

class FreshaConfig(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

class AppConfig(BaseModel):
    fresha: FreshaConfig
    smtp: SMTPConfig
    alert_email: Optional[EmailStr] = None
    timezone: str = 'America/New_York'
    max_retries: int = 3
    retry_delay: int = 5

def validate_config(config_dict: dict) -> AppConfig:
    """Validate configuration using Pydantic"""
    try:
        return AppConfig(**config_dict)
    except Exception as e:
        logger.error(f'Configuration validation failed: {e}')
        raise
