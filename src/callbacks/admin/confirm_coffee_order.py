from aiogram import types
import models
import constants
from markups import markups
from models.coffee_beans_order import CoffeeBeansOrder
import asyncio

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    current_order = await CoffeeBeansOrder.get_current_order()
    await current_order.confirm_by_admin()
    
    # Send notifications to all users with notifications enabled
    users = await models.users.get_users()
    notification_text = (
        "Собран групповой заказ кофейных зерен!\n"
        "Пожалуйста, подтвердите ваше участие в заказе и произведите оплату.\n"
        "Реквизиты для оплаты будут отправлены после подтверждения."
    )
    
    for user in users:
        if await user.notification:
            try:
                await constants.bot.send_message(
                    user.id,
                    notification_text,
                    reply_markup=markups.create([
                        ("✅ Подтвердить участие", f'{{"r":"user"}}confirm_coffee_participation'),
                        ("❌ Отказаться", f'{{"r":"user"}}decline_coffee_participation')
                    ])
                )
            except:
                pass
    
    await callback_query.message.edit_text(
        text="Уведомления о сборе заказа отправлены всем пользователям.",
        reply_markup=markups.create([
            (constants.language.back, f"{constants.JSON_ADMIN}coffee_beans_order")
        ])
    ) 