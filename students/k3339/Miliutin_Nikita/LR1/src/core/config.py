from pydantic import BaseModel


class Settings(BaseModel):
    secret_key: str = "super-secret-key-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60


settings = Settings()