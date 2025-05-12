from aiogram import types
import models
import constants
from markups import markups
from models.coffee_beans_order import CoffeeBeansOrder

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    payment_info = (
        "Для оплаты заказа переведите сумму на следующие реквизиты:\n\n"
        "Сбербанк: 1234 5678 9012 3456\n"
        "Получатель: ООО 'Вкусный Кофе'\n"
        "Назначение платежа: Оплата заказа кофейных зерен"
    )
    
    await callback_query.message.edit_text(
        text=f"Спасибо за подтверждение участия!\n\n{payment_info}",
        reply_markup=markups.create([
            (constants.language.back, f"{constants.JSON_USER}profile")
        ])
    ) 