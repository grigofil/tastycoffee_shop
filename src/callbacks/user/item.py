import importlib
from aiogram import types
import models
import constants
from markups import markups
import asyncio


async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    item = models.items.Item(data["iid"])
    item_text, item_weight, category, image_id, cart_dict, price, discounted_price = await asyncio.gather(
        item.format_text(constants.config["info"]["item_template"], constants.config["settings"]["currency"]),
        item.weight,
        item.category,
        item.image_id,
        user.cart.items.dict,
        item.price,
        item.discounted_price,
    )
    
    # If there's a discount, modify the item_text to show the discounted price
    if price != discounted_price:
        currency = constants.config["settings"]["currency"]
        item_text = item_text.replace(f"{price} {currency}", f"{discounted_price} {currency}")

    def cart_callback(state: int):
        return f'{{"r":"user","iid":{item.id},"s":{state},"d":"item"}}changeCart'


    item_id = str(item.id)

    if item_id in cart_dict:
        cart_buttons = (
            (constants.language.minus, cart_callback(0)),
            (cart_dict[item_id], f'None'),
            (constants.language.plus, cart_callback(1)),
        )
    else:
        cart_buttons = (constants.language.add_to_cart, cart_callback(1))

    del_data = ',"del":"1"'
    back_button = (constants.language.back, f'{{"r":"user","cid":"{category.id}"{del_data if image_id else ""}}}category'),

    if "rd" in data:
        back_button = (constants.language.back, f"{constants.JSON_USER}{data['rd']}")
    markup = markups.create([
        cart_buttons,
        back_button
    ])

    # if image_id:
    #     await callback_query.message.delete()
    #     return await callback_query.message.answer_photo(
    #         photo=image_id,
    #         caption=item_text,
    #         reply_markup=markup
    #     )
    return await callback_query.message.edit_text(
        text=item_text,
        reply_markup=markup
    )

