from aiogram import types
import models
import constants
from markups import markups
import datetime
import asyncio
import database

async def get_registration_stats():
    now = datetime.datetime.now()
    
    # Get all users with their registration dates
    users = await database.fetch("SELECT date_created FROM users")
    
    # Convert dates to datetime objects
    dates = [datetime.datetime.strptime(date[0], constants.TIME_FORMAT) for date in users]
    
    # Calculate stats for different time periods
    daily = sum(1 for date in dates if (now - date).days < 1)
    weekly = sum(1 for date in dates if (now - date).days < 7)
    monthly = sum(1 for date in dates if (now - date).days < 30)
    all_time = len(dates)
    
    return {
        'daily': daily,
        'weekly': weekly,
        'monthly': monthly,
        'all_time': all_time
    }

async def get_order_stats():
    now = datetime.datetime.now()
    
    # Get all orders with their creation dates
    orders = await database.fetch("SELECT date_created FROM orders")
    
    # Convert dates to datetime objects
    dates = [datetime.datetime.strptime(date[0], constants.TIME_FORMAT) for date in orders]
    
    # Calculate stats for different time periods
    daily = sum(1 for date in dates if (now - date).days < 1)
    weekly = sum(1 for date in dates if (now - date).days < 7)
    monthly = sum(1 for date in dates if (now - date).days < 30)
    all_time = len(dates)
    
    return {
        'daily': daily,
        'weekly': weekly,
        'monthly': monthly,
        'all_time': all_time
    }

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    # Get both registration and order stats concurrently
    reg_stats, order_stats = await asyncio.gather(
        get_registration_stats(),
        get_order_stats()
    )
    
    # Format the statistics text
    text = f"""📊 {constants.language.stats}

👥 {constants.language.registration_stats}:
• {constants.language.daily}: {reg_stats['daily']}
• {constants.language.weekly}: {reg_stats['weekly']}
• {constants.language.monthly}: {reg_stats['monthly']}
• {constants.language.all_time}: {reg_stats['all_time']}

📦 {constants.language.order_stats}:
• {constants.language.daily}: {order_stats['daily']}
• {constants.language.weekly}: {order_stats['weekly']}
• {constants.language.monthly}: {order_stats['monthly']}
• {constants.language.all_time}: {order_stats['all_time']}"""

    markup = markups.create([
        (constants.language.back, f"{constants.JSON_ADMIN}adminPanel"),
    ])

    if message:
        return await message.answer(text, reply_markup=markup)
    await callback_query.message.edit_text(text, reply_markup=markup) 