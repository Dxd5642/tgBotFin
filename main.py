import os
from dotenv import load_dotenv
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent

load_dotenv(str(BASE_DIR / ".env"))

BOT_TOKEN = os.getenv("BOT_TOKEN")

from datebase import datebase