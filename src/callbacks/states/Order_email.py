from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups
import re
import states


async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, state: FSMContext, message: types.Message=None) -> None:
    # Only validate email when processing a message, not a callback
    if message:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", message.text):
            await message.answer(constants.language.invalid_email)
            return
        
        await state.update_data(email=message.text)
    
    # Handle callback or continue after email validation
    checkout_settings = constants.config["checkout"]
    markup = [
        (constants.language.skip, f'{{"r":"user"}}skip'),
        (constants.language.back, f'{{"r":"user","d":"cart"}}cancel')
    ]
    text = constants.language.unknown_error
    if checkout_settings["phone"]:
        text = constants.language.input_phone
        await states.Order.phone_number.set()
    elif checkout_settings["adress"]:
        text = constants.language.input_adress
        await states.Order.adress.set()
    elif checkout_settings["captcha"]:
        text = constants.language.input_captcha
        markup = [(constants.language.refresh, f'{{"r":"user"}}refresh')] + markup
        await states.Order.captcha.set()
    else:
        text = constants.language.input_comment
        await states.Order.comment.set()

    if callback_query:
        await callback_query.message.edit_text(
            text=text,
            reply_markup=markups.create(markup)
        )
    elif message:
        await message.answer(
            text=text,
            reply_markup=markups.create(markup)
        )


