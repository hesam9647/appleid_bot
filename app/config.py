from dataclasses import dataclass
from environs import Env
from pathlib import Path

@dataclass
class DbConfig:
    database: str

@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    channel_id: str

@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig

def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMIN_IDS"))),
            channel_id=env.str("CHANNEL_ID")
        ),
        db=DbConfig(
            database=env.str("DATABASE_URL")
        )
    )
