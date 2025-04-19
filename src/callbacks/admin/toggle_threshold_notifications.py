from aiogram import types
import models
import constants
from markups import markups
import importlib

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    current_state = constants.config["notifications"]["order_threshold_enabled"]
    constants.config.set(("notifications", "order_threshold_enabled"), not current_state)
    
    await importlib.import_module("callbacks.admin.notification_settings").execute(callback_query, user, data, message) 