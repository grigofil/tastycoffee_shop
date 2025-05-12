from aiogram import types
from aiogram.dispatcher import FSMContext
import models
import constants
from markups import markups
import datetime
import json
import asyncio
from models.pending_orders import PendingOrdersPool

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, state: FSMContext, message: types.Message=None) -> None:
    call = callback_query.data[callback_query.data.index("}")+1:]
    
    if call != "confirm_order":
        # Handle other possible calls if necessary
        return
    
    # Get all data collected during the order process
    state_data = {}
    if state:
        state_data = await state.get_data()
    
    # Get user's telegram username
    username = await user.username
    
    # Create the order
    cart_items = await user.cart.items.dict
    cart_items_json = []
    
    total_price = 0
    total_bean_coffee_weight = 0  # Total weight of coffee beans in the order
    
    for item_id, amount in cart_items.items():
        item = models.items.Item(item_id)
        item_name, item_price, item_weight, category_name = await asyncio.gather(
            item.name,
            item.price,
            item.weight,
            item.category_name
        )
        
        # Calculate total weight of coffee beans
        if "кофе в зернах" in item_name:
            # Item weight is in grams, convert to kg
            total_bean_coffee_weight += (item_weight / 1000) * amount
        
        cart_items_json.append({
            "id": item_id,
            "amount": amount,
            "title": item_name,
            "price": item_price,
            "category": category_name,
            "weight": item_weight
        })
        
        total_price += item_price * amount
    
    # Create a new order
    order = await models.orders.create(
        user_id=user.id,
        items_json=json.dumps(cart_items_json),
        date_created=datetime.datetime.now(),
        adress=state_data.get("adress"),
        phone_number=state_data.get("phone_number"),
        email=state_data.get("email"),
        comment=state_data.get("comment"),
        username=username
    )
    
    # Add the order to the pending orders pool for supplier
    await PendingOrdersPool.add_order_to_pool(order.id)
    
    # Send notification to all managers about the new order
    all_users = await models.users.get_users()
    
    # Prepare order details for notification
    order_details = f"Новый заказ #{order.id} от {username}\n"
    order_details += f"Сумма заказа: {total_price} {constants.config['settings']['currency_symbol']}\n"
    
    items_text = "Товары:\n"
    for item in cart_items_json:
        # Include category name along with title in the notification
        items_text += f"• {item['title']} ({item['category']}) - {item['amount']} шт. ({item['weight']} г)\n"
    
    order_details += items_text
    
    # Notify all managers
    for user in all_users:
        if await user.is_manager:
            try:
                await constants.bot.send_message(
                    user.id,
                    f"🔔 {order_details}"
                )
            except:
                pass
    
    # Notify admins only if the order contains coffee beans with weight > 25kg
    if total_bean_coffee_weight > 25:
        for user in all_users:
            if await user.is_admin:
                try:
                    await constants.bot.send_message(
                        user.id,
                        f"⚠️ ВНИМАНИЕ! Заказ содержит кофе в зернах с весом более 25 кг!\n\n"
                        f"Общий вес кофе в зернах: {total_bean_coffee_weight:.2f} кг\n\n"
                        f"{order_details}"
                    )
                except:
                    pass
    
    # Clear the cart after successful order
    await user.cart.items.clear()
    
    # Clear the state
    if state:
        await state.finish()
    
    await callback_query.message.edit_text(
        text=constants.language.order_placed_successfully(order.id),
        reply_markup=markups.create([
            (constants.language.back_to_catalog, f"{constants.JSON_USER}catalogue")
        ])
    )


