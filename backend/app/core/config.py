from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Load konfigurasi dari .env, lalu fallback ke default jika tidak diisi.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Agri-Trend DSS", validation_alias="APP_NAME")
    app_version: str = Field(default="1.0.0", validation_alias="APP_VERSION")
    host: str = Field(default="0.0.0.0", validation_alias="HOST")
    port: int = Field(default=8000, validation_alias="PORT")

    allowed_origins_raw: str = Field(default="*", validation_alias="ALLOWED_ORIGINS")
    supabase_url: str = Field(validation_alias="SUPABASE_URL")
    supabase_key: str = Field(validation_alias="SUPABASE_KEY")

    @property
    def allowed_origins(self) -> list[str]:
        # ALLOWED_ORIGINS di .env pakai format CSV: a,b,c
        return [item.strip() for item in self.allowed_origins_raw.split(",") if item.strip()] or ["*"]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
