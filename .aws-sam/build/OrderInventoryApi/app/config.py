from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Explicitly load the .env file for local development
load_dotenv()

# Pydantic Settings provide optional features for loading a settings or config class from environment var/secrets files

class Settings(BaseSettings):
    #local development defaults(from .env)
    database_hostname: str = "localhost"
    database_port: str = "5432"
    database_password: str = "root"  # Local dev password
    database_name: str = "order_inventory"
    database_username: str = "postgres"

     # AWS production values (from Lambda environment variables)
    db_host: str | None = None
    db_user: str | None = None
    db_pass: str | None = None

    #JWT configuration
    secret_key: str = "secret"
    secret_key_admin: str = "admin-secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Allow extra environment variables
    )

    @property
    def database_url(self):
        """Returns appropriate URL based on environment"""
        if self.db_host:  # Production AWS environment
            return f"postgresql://{self.db_user}:{self.db_pass}@{self.db_host}/{self.database_name}"
        
        # Local development
        return f"postgresql://{self.database_username}:{self.database_password}@" \
               f"{self.database_hostname}:{self.database_port}/{self.database_name}"



settings = Settings()