from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/santa"
    
    # Auth
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # OpenAI / GPT Configuration
    openai_api_key: str = ""
    gpt_model: str = "gpt-4o"
    gpt_extraction_model: str = "gpt-4o-mini"
    gpt_safety_model: str = "gpt-4o-mini"  # Model for email safety checks
    email_safety_check_enabled: bool = True  # Enable/disable email safety checks
    
    # Email - Incoming (POP3/IMAP)
    pop3_server: str = ""
    pop3_port: int = 995
    pop3_use_ssl: bool = True
    pop3_username: str = ""
    pop3_password: str = ""
    
    # Email - Outgoing (SMTP)
    smtp_server: str = ""
    smtp_port: int = 587
    smtp_use_tls: bool = True
    smtp_username: str = ""
    smtp_password: str = ""
    santa_email_address: str = ""
    santa_display_name: str = "Santa Claus"
    
    # Worker settings
    worker_poll_interval: int = 5  # seconds between job checks
    email_fetch_interval: int = 60  # seconds between email fetches
    
    # Invite-only registration (Ed25519 public key in PEM format)
    invite_public_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
