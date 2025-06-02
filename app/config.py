from dataclasses import dataclass
from environs import Env
from typing import List

@dataclass
class DbConfig:
    database_url: str

@dataclass
class TgBot:
    token: str
    admin_ids: List[int]

@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig

def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=[int(id.strip()) for id in env.str("ADMIN_IDS").split(",")]
        ),
        db=DbConfig(
            database_url=env.str("DATABASE_URL")
        )
    )
