import logging.config

from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml


class Settings(BaseSettings):
    SECRET: str
    EXPIRE_TIME: int
    ALGORITHM: str
    S3_CLOUD_KEY: str
    S3_CLOUD_SECRET: str
    BUCKET_NAME: str
    BUCKET_PUBLIC_PATH: str
    MODE: int
    ACCESS_TOKEN: str

    @property
    def mode(self):
        if self.MODE == 1:
            return True
        else:
            return False

    model_config = SettingsConfigDict(env_file=".env")


with open('logging.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

settings = Settings()
