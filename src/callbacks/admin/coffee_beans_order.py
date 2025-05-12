from aiogram import types
import models
import constants
from markups import markups
from models.coffee_beans_order import CoffeeBeansOrder

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    current_order = await CoffeeBeansOrder.get_current_order()
    total_weight = await current_order.get_total_weight()
    status = await current_order.get_status()
    
    min_order_weight = constants.config.get("coffee_beans", "min_order_weight", 25.0)
    
    text = f"Текущий статус сбора заказа на кофейные зерна:\n\n"
    text += f"Общий вес: {total_weight:.2f} кг\n"
    text += f"Минимальный заказ: {min_order_weight} кг\n"
    text += f"Статус: {status}\n"
    
    markup = []
    
    if status == 'collecting' and total_weight >= min_order_weight:
        markup.append((
            "✅ Подтвердить сбор заказа",
            f'{{"r":"admin"}}confirm_coffee_order'
        ))
    
    markup.append((constants.language.back, f"{constants.JSON_ADMIN}settings"))
    
    if message:
        return await message.answer(text=text, reply_markup=markups.create(markup))
    
    await callback_query.message.edit_text(
        text=text,
        reply_markup=markups.create(markup)
    ) 