from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "UP Maternal Care API"
    api_v1_prefix: str = "/api/v1"
    environment: str = "development"
    database_url: str = "sqlite:///./up_maternal_care_v2.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
