from aiogram import types
import asyncio
import models
import constants
from markups import markups


async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    category = models.categories.Category(data["cid"])
    name, children, items, parent_id = await asyncio.gather(category.name, category.children, category.items, category.parent_id)

    markup = [
        (await child.name, f'{{"r":"user", "cid":{child.id}}}category')
        for child in children
    ]
    for item in items:
        name_i, price, discount_price, weight = await asyncio.gather(item.name, item.price, item.discounted_price, item.weight)
        display_price = discount_price
        price_text = f'{display_price}₽'
        if display_price != price:
            price_text = f'{display_price}₽'
        markup.append((f'{price_text} за {weight}г {name_i}', f'{{"r":"user","iid":{item.id}}}item'))
    if parent_id:
        markup.append((constants.language.back, f'{{"r":"user","cid":{parent_id}}}category'))
    else:
        markup.append((constants.language.back, f'{constants.JSON_USER}catalogue'))

    text=name
    if not children and not items:
        text = f"{name}\n\n{constants.language.category_is_empty}"

    if "del" in data:
        await callback_query.message.delete()
        return await callback_query.message.answer(
            text=text,
            reply_markup=markups.create(markup)
        )
    await callback_query.message.edit_text(
        text=text,
        reply_markup=markups.create(markup)
    )


