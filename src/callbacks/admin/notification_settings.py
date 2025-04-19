from aiogram import types
import models
import constants
from markups import markups
import states

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    config = constants.config["notifications"]
    threshold_enabled = config["order_threshold_enabled"]
    current_threshold = config["order_threshold"]
    currency_symbol = constants.config["settings"]["currency_symbol"]
    
    text = (
        "📊 Настройки уведомлений\n\n"
        f"Уведомление о превышении суммы заказов: {'✅ Включено' if threshold_enabled else '❌ Выключено'}\n"
        f"Текущий порог: {current_threshold:.2f} {currency_symbol}"
    )
    
    markup = markups.create([
        (
            "❌ Выключить уведомления" if threshold_enabled else "✅ Включить уведомления",
            f"{constants.JSON_ADMIN}toggle_threshold_notifications"
        ),
        ("💰 Изменить пороговое значение", f"{constants.JSON_ADMIN}change_threshold"),
        (constants.language.back, f"{constants.JSON_ADMIN}settings"),
    ])

    if message:
        return await message.answer(text, reply_markup=markup)
    await callback_query.message.edit_text(text, reply_markup=markup) 