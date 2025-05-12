from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups
import states

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, state: FSMContext, message: types.Message=None) -> None:
    # Only update comment when handling a message
    if message:
        await state.update_data(comment=message.text)
    
    # Get all collected data
    data = await state.get_data()
    
    # Get username
    username = await user.username
    
    # Set next state
    await states.Order.confirmation.set()
    
    # Create markup
    markup = markups.create([
        (constants.language.place_order, f'{{"r":"user"}}confirm_order'),
        (constants.language.back, f'{{"r":"user","d":"cart"}}cancel')
    ])
    
    # Create confirmation text
    text = constants.language.confirm_order(
        email=data.get("email"),
        phone_number=data.get("phone_number"),
        adress=data.get("adress"),
        comment=data.get("comment"),
        username=username
    )
    
    # Handle response based on context
    if callback_query:
        await callback_query.message.edit_text(
            text=text,
            reply_markup=markup
        )
    elif message:
        await message.answer(
            text=text,
            reply_markup=markup
        )


