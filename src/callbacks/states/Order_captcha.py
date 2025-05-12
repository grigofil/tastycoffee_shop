from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups
import states

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, state: FSMContext, message: types.Message=None) -> None:
    # This is a placeholder implementation - captcha verification goes here
    # For now, we'll just proceed to the next step
    
    # Set next state regardless of context
    await states.Order.confirmation.set()
    
    # Handle captcha verification if message exists
    if message:
        # TODO: Implement actual captcha verification here
        captcha_valid = True  # Placeholder
        
        if not captcha_valid:
            await message.answer(constants.language.input_captcha_error)
            return
    
    # Get all collected data
    data = await state.get_data()
    
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


