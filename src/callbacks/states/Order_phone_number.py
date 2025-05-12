from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups
import states
import re


async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, state: FSMContext, message: types.Message=None) -> None:
    # Only validate phone when processing a message
    if message:
        if re.match(r"^(\+7|8)\d{10}$", message.text):
            await message.answer(constants.language.input_phone_error)
            return

        await state.update_data(phone_number=message.text)

    # Handle callback or continue after phone validation
    checkout_settings = constants.config["checkout"]

    text = constants.language.unknown_error
    if checkout_settings["adress"]:
        text = constants.language.input_adress
        await states.Order.adress.set()
    else:
        text = constants.language.input_comment
        await states.Order.comment.set()

    if callback_query:
        await callback_query.message.edit_text(
            text=text,
            reply_markup=markups.create([
                (constants.language.skip, f'{{"r":"user"}}skip'),
                (constants.language.back, f'{{"r":"user","d":"cart"}}cancel')
            ])
        )
    elif message:
        await message.answer(
            text=text,
            reply_markup=markups.create([
                (constants.language.skip, f'{{"r":"user"}}skip'),
                (constants.language.back, f'{{"r":"user","d":"cart"}}cancel')
            ])
        )


