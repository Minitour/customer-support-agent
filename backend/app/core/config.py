from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/support_agent"
    SECRET_KEY: str = "supersecretkey-change-in-production"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 30
    ALGORITHM: str = "HS256"

    OPENAI_API_KEY: str = ""

    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001

    FRONTEND_URL: str = "http://localhost:5173"

    PRODUCTS_JSON_PATH: str = "/app/.data/products.json"
    POLICY_DIR_PATH: str = "/app/.data/policy"


settings = Settings()
