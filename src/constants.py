import importlib

import aiogram
from config import config
import os
import asyncio

# Force config initialization if file doesn't exist
if not os.path.exists("config.json"):
    config.init()
    print("Created new config.json file")

# Verify settings section exists, reinitialize if missing
try:
    _ = config["settings"]["currency_symbol"]
except (KeyError, FileNotFoundError):
    print("Config file corrupted or missing settings, reinitializing...")
    config.init()

# Add coffee_beans configuration if it doesn't exist
if "coffee_beans" not in config:
    config.set("coffee_beans", {
        "min_order_weight": 25.0  # Minimum order weight in kg
    })

import localization.ru as language
# language = importlib.import_module(f"localization.{config['settings']['language']}")

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
STATUS_DICT = {
    0: language.status_processing,
    1: language.status_delivery,
    2: language.status_done,
    -1: language.status_cancelled,
}

JSON_USER = '{"r": "user"}'
JSON_MANAGER = '{"r": "manager"}'
JSON_ADMIN = '{"r": "admin"}'

loop = asyncio.new_event_loop()

bot = None
def create_bot(token: str) -> aiogram.bot.bot.Bot:
    global bot
    bot = aiogram.Bot(token=token, loop=loop)
    return bot

