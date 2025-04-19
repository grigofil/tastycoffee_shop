from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, state: FSMContext, message: types.Message=None) -> None:
    call = callback_query.data[callback_query.data.index("}")+1:]
    state_data = await state.get_data()

    # Create the order from state data
    new_order = await models.orders.Order.create_from_state(state_data)
    
    await callback_query.message.edit_text(
        text=constants.language.order_confirmed,
        reply_markup=markups.create([
            [{"text": constants.language.back_to_menu, "callback_data": "menu"}]
        ])
    )

    # After creating the order, check if we need to notify admins
    order_value = await new_order.total_value
    await models.orders.notify_admins_if_threshold_exceeded(order_value)


