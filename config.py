import os.path

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: SecretStr = os.getenv('BOT_TOKEN')
    project_path: str = os.path.dirname(os.path.abspath(__file__))
    chapters_json_pattern: str = r"__DATA__ = (.*);"
    ranobe_host: str = "https://ranobelib.me"
    regex: str = r"^(http[s]?:\/\/)(ranobelib.me\/)([\w\-\.]+[^#?\s]+)(.*)?(#[\w\-]+)?$"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


config = Settings()
