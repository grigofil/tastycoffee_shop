from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups
import importlib

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, state: FSMContext, message: types.Message=None) -> None:
    if not message.text.replace(".", "", 1).isdigit():
        await message.answer("Пороговое значение должно быть числом")
        return
        
    new_threshold = float(message.text)
    constants.config.set(("notifications", "order_threshold"), new_threshold)
    
    await state.finish()
    await importlib.import_module("callbacks.admin.notification_settings").execute(callback_query, user, data, message) 