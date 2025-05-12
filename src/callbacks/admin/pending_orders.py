from aiogram import types
import models
import constants
from markups import markups
from models.pending_orders import PendingOrdersPool
import asyncio

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    # Check if there's a specific order to mark as processed
    if "process_order" in data:
        order_id = int(data["process_order"])
        await PendingOrdersPool.mark_order_as_processed(order_id)
        # Return to the main pending orders view
        data.pop("process_order")
    
    # Get all pending orders and statistics
    pending_orders = await PendingOrdersPool.get_all_pending_orders()
    stats = await PendingOrdersPool.get_statistics()
    
    # Format text with statistics
    text = "📋 Ожидающие заказы (для оформления заказа поставщику)\n\n"
    
    # Add statistics
    text += f"Всего ожидающих заказов: {stats['status_counts'].get('pending', 0)}\n"
    text += f"Обработанных заказов: {stats['status_counts'].get('processed', 0)}\n"
    text += f"Всего товаров в ожидающих заказах: {stats['total_pending_items']}\n\n"
    
    # Format the orders list
    if pending_orders:
        text += "Список ожидающих заказов:\n"
        for i, order in enumerate(pending_orders[:10], 1):  # Show first 10 orders
            order_items = await asyncio.gather(*[order.__items_json])
            items_count = len(order_items[0]) if order_items and order_items[0] else 0
            text += f"{i}. Заказ #{order.id} - {items_count} товаров\n"
        
        if len(pending_orders) > 10:
            text += f"... и еще {len(pending_orders) - 10} заказов\n"
    else:
        text += "Нет ожидающих заказов.\n"
    
    # Create markup with buttons for each order
    markup = []
    for order in pending_orders[:10]:  # Show buttons for first 10 orders
        markup.append((
            f"Обработать заказ #{order.id}",
            f'{{"r":"admin","process_order":{order.id}}}pending_orders'
        ))
    
    markup.append((constants.language.back, f"{constants.JSON_ADMIN}settings"))
    
    if message:
        return await message.answer(text=text, reply_markup=markups.create(markup))
    
    await callback_query.message.edit_text(
        text=text,
        reply_markup=markups.create(markup)
    ) 