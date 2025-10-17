from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or a .env file.
    """
    # Application constants
    DATAPOINTS_CHUNK: int = 40000

    # InfluxDB Connection Details
    INFLUX_URL: str = "http://localhost:8086"
    INFLUX_ORG: str = "data"
    INFLUX_TOKEN: str = "changeme"


    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

# Create a single instance that the rest of your app can import
settings = Settings()