from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str
    allowed_user_id: int
    model_config = SettingsConfigDict(
        env_file=".env"
    )

settings = Settings()