from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups
import states

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, state: FSMContext, message: types.Message=None) -> None:
    # Only process adress when handling a message
    if message:
        await state.update_data(adress=message.text)
    
    # Set next state
    await states.Order.comment.set()
    
    # Prepare markup
    markup = markups.create([
        (constants.language.skip, f'{{"r":"user"}}skip'),
        (constants.language.back, f'{{"r":"user","d":"cart"}}cancel')
    ])
    
    # Handle response based on context
    if callback_query:
        await callback_query.message.edit_text(
            text=constants.language.input_comment,
            reply_markup=markup
        )
    elif message:
        await message.answer(
            text=constants.language.input_comment,
            reply_markup=markup
        )

