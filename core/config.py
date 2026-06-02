from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_NAME: str
    
    REDIS_HOST: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:5432/{self.DB_NAME}"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra='ignore'
    )


settings = Settings()
