from aiogram import types
import models
import constants
from markups import markups
import datetime
import asyncio
import matplotlib.pyplot as plt
from io import BytesIO
import localization.ru as language


async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    text = constants.language.stats
    markup = markups.create([
        (constants.language.registration_stats, f"{constants.JSON_ADMIN}registration_stats"),
        (constants.language.order_stats, f"{constants.JSON_ADMIN}order_stats"),
        (language.order_summary, f"{constants.JSON_ADMIN}order_summary"),
        (constants.language.back, f"{constants.JSON_ADMIN}adminPanel"),
    ])

    if message:
        return await message.answer(text, reply_markup=markup)
    await callback_query.message.edit_text(text, reply_markup=markup)


async def get_users_stats(period=None):
    """Get user registration statistics for a specific time period"""
    all_users = await models.users.get_users()
    now = datetime.datetime.now()
    
    if period == 'daily':
        cutoff_date = now - datetime.timedelta(days=1)
    elif period == 'weekly':
        cutoff_date = now - datetime.timedelta(days=7)
    elif period == 'monthly':
        cutoff_date = now - datetime.timedelta(days=30)
    else:  # all time
        cutoff_date = datetime.datetime.min
    
    user_stats = [user for user in all_users if await user.date_created >= cutoff_date]
    return user_stats


async def get_orders_stats(period=None):
    """Get order statistics for a specific time period"""
    statuses = [0, 1, 2, -1]  # Processing, Delivery, Done, Cancelled
    now = datetime.datetime.now()
    
    if period == 'daily':
        cutoff_date = now - datetime.timedelta(days=1)
    elif period == 'weekly':
        cutoff_date = now - datetime.timedelta(days=7)
    elif period == 'monthly':
        cutoff_date = now - datetime.timedelta(days=30)
    else:  # all time
        cutoff_date = datetime.datetime.min
    
    orders_by_status = {}
    total_revenue = 0
    
    for status in statuses:
        orders_list = await models.orders.get_orders_by_status(status)
        filtered_orders = []
        
        for order in orders_list:
            if await order.date_created >= cutoff_date:
                filtered_orders.append(order)
                
                # Calculate revenue for completed orders
                if status == 2:  # Only count completed orders for revenue
                    items = await order.items
                    order_total = sum(item.price * item.amount for item in items)
                    total_revenue += order_total
        
        orders_by_status[status] = filtered_orders
    
    return orders_by_status, total_revenue


async def generate_pie_chart(sizes, labels, title):
    """Generate a pie chart from the provided data"""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    ax.set_title(title)
    
    # Save the chart to a buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close(fig)
    
    return buffer


async def get_order_items_summary():
    """Get a summary of all items in current orders"""
    # Get orders with statuses 0 (Processing) and 1 (Delivery)
    processing_orders = await models.orders.get_orders_by_status(0)
    delivery_orders = await models.orders.get_orders_by_status(1)
    
    all_current_orders = processing_orders + delivery_orders
    
    # Aggregate items across all orders
    items_summary = {}  # {item_id: {"title": "", "total_amount": 0}}
    
    for order in all_current_orders:
        items = await order.items
        for item in items:
            item_id = item.id
            if item_id not in items_summary:
                # Get the category name for this item
                original_item = models.items.Item(int(item_id))
                category_name = await original_item.category_name
                
                items_summary[item_id] = {
                    "title": item.title,
                    "price": item.price,
                    "total_amount": 0,
                    "category": category_name
                }
            items_summary[item_id]["total_amount"] += item.amount
    
    # Sort by total amount (descending)
    sorted_items = sorted(
        items_summary.items(), 
        key=lambda x: x[1]["total_amount"], 
        reverse=True
    )
    
    return sorted_items 