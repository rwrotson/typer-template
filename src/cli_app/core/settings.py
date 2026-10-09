from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Load application settings from CLI_APP_* variables and .env."""

    model_config = SettingsConfigDict(
        env_prefix="CLI_APP_",
        env_file=".env",
        extra="ignore",
    )
