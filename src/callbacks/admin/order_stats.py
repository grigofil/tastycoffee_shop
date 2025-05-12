from aiogram import types
import models
import constants
from markups import markups
import datetime
import asyncio
import matplotlib.pyplot as plt
from io import BytesIO
import localization.ru as language
from callbacks.admin.stats import get_orders_stats, generate_pie_chart


async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    period = data.get('period', 'all')
    
    if period == 'all':
        # Show period selection menu
        text = constants.language.order_stats
        markup = markups.create([
            (constants.language.all_time, f'{{"r":"admin","period":"all_time"}}order_stats'),
            (constants.language.monthly, f'{{"r":"admin","period":"monthly"}}order_stats'),
            (constants.language.weekly, f'{{"r":"admin","period":"weekly"}}order_stats'),
            (constants.language.daily, f'{{"r":"admin","period":"daily"}}order_stats'),
            (constants.language.back, f"{constants.JSON_ADMIN}stats"),
        ])
        
        await callback_query.message.edit_text(text, reply_markup=markup)
        return
    
    # Process period stats
    if period == 'all_time':
        period_key = None
        title = constants.language.all_time
    elif period == 'monthly':
        period_key = 'monthly'
        title = constants.language.monthly
    elif period == 'weekly':
        period_key = 'weekly'
        title = constants.language.daily
    elif period == 'daily':
        period_key = 'daily'
        title = constants.language.daily
    
    # Fetch statistics
    orders_by_status, total_revenue = await get_orders_stats(period_key)
    
    # Basic statistics
    processing_orders = len(orders_by_status.get(0, []))
    delivery_orders = len(orders_by_status.get(1, []))
    completed_orders = len(orders_by_status.get(2, []))
    cancelled_orders = len(orders_by_status.get(-1, []))
    total_orders = processing_orders + delivery_orders + completed_orders + cancelled_orders
    
    # Prepare text message
    text = f"{constants.language.order_stats} ({title}):\n\n"
    text += f"📦 {language.total_orders}: {total_orders}\n"
    text += f"💰 {language.total_revenue}: {total_revenue:.2f} {constants.config['settings']['currency_symbol']}\n\n"
    
    text += f"⌛ {constants.STATUS_DICT[0]}: {processing_orders}\n"
    text += f"🚚 {constants.STATUS_DICT[1]}: {delivery_orders}\n"
    text += f"✅ {constants.STATUS_DICT[2]}: {completed_orders}\n"
    text += f"❌ {constants.STATUS_DICT[-1]}: {cancelled_orders}\n"
    
    # Create a pie chart of order statuses
    if total_orders > 0:
        # Order status distribution
        labels = []
        sizes = []
        
        if processing_orders > 0:
            labels.append(constants.STATUS_DICT[0])
            sizes.append(processing_orders)
        if delivery_orders > 0:
            labels.append(constants.STATUS_DICT[1])
            sizes.append(delivery_orders)
        if completed_orders > 0:
            labels.append(constants.STATUS_DICT[2])
            sizes.append(completed_orders)
        if cancelled_orders > 0:
            labels.append(constants.STATUS_DICT[-1])
            sizes.append(cancelled_orders)
        
        if len(sizes) > 1:  # Only create a chart if we have at least 2 different statuses
            chart_title = f"{language.order_status_distribution} ({title})"
            chart_buffer = await generate_pie_chart(sizes, labels, chart_title)
            
            # Send the chart as a photo
            await callback_query.message.delete()
            await callback_query.message.answer_photo(
                types.InputFile(chart_buffer, filename='order_stats.png'),
                caption=text,
                reply_markup=markups.create([
                    (constants.language.back, f"{constants.JSON_ADMIN}order_stats")
                ])
            )
            return
    
    # If we don't have enough data for a chart, just show text stats
    await callback_query.message.edit_text(
        text=text,
        reply_markup=markups.create([
            (constants.language.back, f"{constants.JSON_ADMIN}order_stats")
        ])
    ) 