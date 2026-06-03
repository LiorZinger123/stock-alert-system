from pydantic_settings import BaseSettings, SettingsConfigDict


class EmailSettings(BaseSettings):
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra='ignore'
    )

email_settings = EmailSettings()
