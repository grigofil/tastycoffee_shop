from aiogram import types
import models
import constants
from markups import markups
import states

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    # Redirect to the state handler for Order confirmation
    from callbacks.states.Order_confirmation import execute as state_execute
    await state_execute(callback_query, user, data, None, message) 