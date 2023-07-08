from pathlib import Path
from dotenv import load_dotenv
from os import getenv
from os.path import exists
from functools import lru_cache

@lru_cache()
def init():
    path = Path(__file__).parent.parent
    if exists(path.parent/".env"):
        load_dotenv(dotenv_path=path.parent/".env")
    return path

def get_env(env_name: str):
    res = getenv(env_name)
    if not res:
        raise Exception(env_name+" variable not found")
    return res
