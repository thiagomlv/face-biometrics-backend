from pydantic_settings import BaseSettings, SettingsConfigDict

# ======================================
#   DB Settings
# ======================================
class DataBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.db")

    DB_HOST: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_PORT: str


# ======================================
#   Instance to be exported
# ======================================
settings = DataBaseSettings()

# ======================================
#   Tests
# ======================================
if __name__ == "__main__":
    print(f"Host: {settings.DB_HOST}")
    print(f"Name: {settings.DB_NAME}")
    print(f"User: {settings.DB_USER}")
    print(f"Password: {settings.DB_PASSWORD}")
    print(f"Port: {settings.DB_PORT}")