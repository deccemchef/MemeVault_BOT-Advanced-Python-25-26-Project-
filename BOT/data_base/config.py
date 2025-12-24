import os
import ssl
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv

DOTENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(DOTENV_PATH)


def _require(name: str) -> str:
    value = os.getenv(name)
    if value is None or value == "":
        raise RuntimeError(f"{name} is not set. Check {DOTENV_PATH}")
    return value


DB_HOST = _require("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", "6432"))
DB_NAME = _require("DB_NAME")
DB_USER = _require("DB_USER")
DB_PASSWORD = _require("DB_PASSWORD")

CA_CERT_PATH = Path(os.getenv("DB_CA_CERT", "~/.postgresql/root.crt")).expanduser()
SSL_CONTEXT = ssl.create_default_context(cafile=str(CA_CERT_PATH))

DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

BOT_TOKEN = _require("BOT_TOKEN")