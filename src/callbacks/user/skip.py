from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups
import states

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    # Get current state
    state = callback_query.bot.get('dp').current_state(user=callback_query.from_user.id)
    current_state = await state.get_state()
    
    if current_state:
        # Handle different states
        if current_state == states.Order.email.state:
            # Skip email input
            await state.update_data(email="")
            
            # Determine next screen based on config
            checkout_settings = constants.config["checkout"]
            if checkout_settings["phone"]:
                await states.Order.phone_number.set()
                
                await callback_query.message.edit_text(
                    text=constants.language.input_phone,
                    reply_markup=markups.create([
                        (constants.language.skip, f'{{"r":"user"}}skip'),
                        (constants.language.back, f'{{"r":"user","d":"cart"}}cancel')
                    ])
                )
            elif checkout_settings["adress"]:
                await states.Order.adress.set()
                
                await callback_query.message.edit_text(
                    text=constants.language.input_adress,
                    reply_markup=markups.create([
                        (constants.language.skip, f'{{"r":"user"}}skip'),
                        (constants.language.back, f'{{"r":"user","d":"cart"}}cancel')
                    ])
                )
            else:
                await states.Order.comment.set()
                
                await callback_query.message.edit_text(
                    text=constants.language.input_comment,
                    reply_markup=markups.create([
                        (constants.language.skip, f'{{"r":"user"}}skip'),
                        (constants.language.back, f'{{"r":"user","d":"cart"}}cancel')
                    ])
                )
                
        elif current_state == states.Order.phone_number.state:
            # Skip phone number input
            await state.update_data(phone_number="")
            
            # Determine next screen based on config
            checkout_settings = constants.config["checkout"]
            if checkout_settings["adress"]:
                await states.Order.adress.set()
                
                await callback_query.message.edit_text(
                    text=constants.language.input_adress,
                    reply_markup=markups.create([
                        (constants.language.skip, f'{{"r":"user"}}skip'),
                        (constants.language.back, f'{{"r":"user","d":"cart"}}cancel')
                    ])
                )
            else:
                await states.Order.comment.set()
                
                await callback_query.message.edit_text(
                    text=constants.language.input_comment,
                    reply_markup=markups.create([
                        (constants.language.skip, f'{{"r":"user"}}skip'),
                        (constants.language.back, f'{{"r":"user","d":"cart"}}cancel')
                    ])
                )
                
        elif current_state == states.Order.adress.state:
            # Skip address input
            await state.update_data(adress="")
            
            # Go to comment input
            await states.Order.comment.set()
            
            await callback_query.message.edit_text(
                text=constants.language.input_comment,
                reply_markup=markups.create([
                    (constants.language.skip, f'{{"r":"user"}}skip'),
                    (constants.language.back, f'{{"r":"user","d":"cart"}}cancel')
                ])
            )
            
        elif current_state == states.Order.comment.state:
            # Skip comment input
            await state.update_data(comment="")
            
            # Go to confirmation screen
            await states.Order.confirmation.set()
            
            # Get all collected data
            data = await state.get_data()
            
            # Get username
            username = await user.username
            
            # Create confirmation text
            text = constants.language.confirm_order(
                email=data.get("email", ""),
                phone_number=data.get("phone_number", ""),
                adress=data.get("adress", ""),
                comment=data.get("comment", ""),
                username=username
            )
            
            await callback_query.message.edit_text(
                text=text,
                reply_markup=markups.create([
                    (constants.language.place_order, f'{{"r":"user"}}confirm_order'),
                    (constants.language.back, f'{{"r":"user","d":"cart"}}cancel')
                ])
            ) 