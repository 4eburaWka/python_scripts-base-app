import os

from dotenv import load_dotenv

from configs import constants


dotenv_path = ".env"
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


def getenv(name: str) -> str:
    env = os.getenv(name)

    if env is None:
        raise ValueError(f"{name} is None")
    return env


def parse_env(env: str):
    match env:
        case constants.LOCAL_ENV | constants.DEV_ENV | constants.PROD_ENV:
            return env
        case _:
            raise ValueError("Env must be one of: local, dev, prod")


ENV = parse_env(getenv("ENV"))

# DATABASE
DB_NAME = getenv("DB_NAME")
DB_USER = getenv("DB_USER")
DB_PASSWORD = getenv("DB_PASSWORD")
DB_HOST = getenv("DB_HOST")
DB_PORT = getenv("DB_PORT")

# REDIS
REDIS_HOST = getenv("REDIS_HOST")
REDIS_PORT = getenv("REDIS_PORT")
REDIS_PASSWORD = getenv("REDIS_PASSWORD")
REDIS_DB = getenv("REDIS_DB")
