from aiogram import types
import models
import constants
from markups import markups
import states


async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    checkout_settings = constants.config['checkout']
    text = constants.language.unknown_error
    
    markup = []
    if checkout_settings["email"]:
        text = constants.language.input_email
        markup = [
            (constants.language.skip, f'{{"r":"user"}}skip'),
            (constants.language.back, f'{{"r":"user","d":"cart"}}cancel')
        ]
        await states.Order.email.set()
    elif checkout_settings["phone"]:
        text = constants.language.input_phone
        markup = [
            (constants.language.skip, f'{{"r":"user"}}skip'),
            (constants.language.back, f'{{"r":"user","d":"cart"}}cancel')
        ]
        await states.Order.phone_number.set()
    elif checkout_settings["adress"]:
        text = constants.language.input_adress
        markup = [
            (constants.language.skip, f'{{"r":"user"}}skip'),
            (constants.language.back, f'{{"r":"user","d":"cart"}}cancel')
        ]
        await states.Order.adress.set()
    elif checkout_settings["captcha"]:
        text = constants.language.input_captcha
        markup = [
            (constants.language.refresh, f'{{"r":"user"}}refresh'),
            (constants.language.back, f'{{"r":"user","d":"cart"}}cancel')
        ]
        await states.Order.captcha.set()
    else:
        text = constants.language.input_comment
        markup = [
            (constants.language.skip, f'{{"r":"user"}}skip'),
            (constants.language.back, f'{{"r":"user","d":"cart"}}cancel')
        ]
        await states.Order.comment.set()
        

    await callback_query.message.edit_text(
        text=text,
        reply_markup=markups.create(markup)
    )


