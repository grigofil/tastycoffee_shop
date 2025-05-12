from aiogram import types
import models
import constants
from markups import markups
import asyncio

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    # Получаем все заказы пользователя
    user_orders = await user.orders
    
    # Разделяем заказы на категории по статусу
    active_orders = []  # Статусы 0 (обработка) и 1 (доставка)
    completed_orders = []  # Статус 2 (выполнен)
    cancelled_orders = []  # Статус -1 (отменен)
    
    for order in user_orders:
        status = await order.status
        if status == 0 or status == 1:
            active_orders.append(order)
        elif status == 2:
            completed_orders.append(order)
        elif status == -1:
            cancelled_orders.append(order)
    
    # Формируем текст для отображения
    text = f"📦 {constants.language.my_orders}\n\n"
    
    # Активные заказы
    if active_orders:
        text += f"🔄 <b>Активные заказы ({len(active_orders)}):</b>\n"
        for order in active_orders:
            order_id = order.id
            order_date = await order.date_created
            order_status = await order.status
            order_items = await order.items
            
            # Подсчитываем общую сумму заказа
            total_price = sum(item.price * item.amount for item in order_items)
            
            # Определяем статус заказа
            status_text = constants.STATUS_DICT.get(order_status, "Неизвестный статус")
            
            text += f"<b>Заказ #{order_id} от {order_date.strftime('%d.%m.%Y')}</b>\n"
            text += f"Статус: {status_text}\n"
            text += f"Сумма: {total_price:.2f} {constants.config['settings']['currency_symbol']}\n"
            
            # Добавляем подробную информацию о товарах в заказе
            text += f"<b>Товары в заказе:</b>\n"
            for item in order_items:
                # Получаем информацию о категории товара
                original_item = models.items.Item(item.id)
                category_name = await original_item.category_name
                
                text += f"• {category_name} {item.title} - {item.amount} шт. x {item.price:.2f} = {item.price * item.amount:.2f} {constants.config['settings']['currency_symbol']}\n"
            
            text += "\n"
    else:
        text += "🔄 <b>Активных заказов нет</b>\n\n"
    
    # Завершенные заказы
    if completed_orders:
        text += f"✅ <b>Выполненные заказы ({len(completed_orders)}):</b>\n"
        for order in completed_orders[:3]:  # Показываем только последние 3 завершенных заказа
            order_id = order.id
            order_date = await order.date_created
            order_items = await order.items
            
            # Подсчитываем общую сумму заказа
            total_price = sum(item.price * item.amount for item in order_items)
            
            text += f"<b>Заказ #{order_id} от {order_date.strftime('%d.%m.%Y')}</b>\n"
            text += f"Сумма: {total_price:.2f} {constants.config['settings']['currency_symbol']}\n"
            
            # Добавляем подробную информацию о товарах в заказе
            text += f"<b>Товары в заказе:</b>\n"
            for item in order_items:
                # Получаем информацию о категории товара
                original_item = models.items.Item(item.id)
                category_name = await original_item.category_name
                
                text += f"• {item.title} (Категория: {category_name}) - {item.amount} шт. x {item.price:.2f} = {item.price * item.amount:.2f} {constants.config['settings']['currency_symbol']}\n"
            
            text += "\n"
        
        if len(completed_orders) > 3:
            text += f"... и еще {len(completed_orders) - 3} завершенных заказов\n\n"
    else:
        text += "✅ <b>Выполненных заказов нет</b>\n\n"
    
    # Отмененные заказы
    if cancelled_orders:
        text += f"❌ <b>Отмененные заказы ({len(cancelled_orders)}):</b>\n"
        for order in cancelled_orders[:3]:  # Показываем только последние 3 отмененных заказа
            order_id = order.id
            order_date = await order.date_created
            order_items = await order.items
            
            # Подсчитываем общую сумму заказа
            total_price = sum(item.price * item.amount for item in order_items)
            
            text += f"<b>Заказ #{order_id} от {order_date.strftime('%d.%m.%Y')}</b>\n"
            text += f"Сумма: {total_price:.2f} {constants.config['settings']['currency_symbol']}\n"
            
            # Добавляем подробную информацию о товарах в заказе
            text += f"<b>Товары в заказе:</b>\n"
            for item in order_items:
                # Получаем информацию о категории товара
                original_item = models.items.Item(item.id)
                category_name = await original_item.category_name
                
                text += f"• {item.title} (Категория: {category_name}) - {item.amount} шт. x {item.price:.2f} = {item.price * item.amount:.2f} {constants.config['settings']['currency_symbol']}\n"
            
            text += "\n"
        
        if len(cancelled_orders) > 3:
            text += f"... и еще {len(cancelled_orders) - 3} отмененных заказов\n"
    
    # Создаем кнопки для навигации
    markup = [
        (constants.language.back, f"{constants.JSON_USER}profile")
    ]
    
    # Отправляем ответ
    try:
        if message:
            await message.answer(text=text, reply_markup=markups.create(markup), parse_mode="HTML")
        else:
            await callback_query.message.edit_text(text=text, reply_markup=markups.create(markup), parse_mode="HTML")
    except Exception as e:
        # Если текст слишком длинный для отправки, сократим его
        short_text = f"📦 {constants.language.my_orders}\n\n"
        short_text += "⚠️ Список заказов слишком большой для отображения всех деталей.\n"
        short_text += f"Активных заказов: {len(active_orders)}\n"
        short_text += f"Выполненных заказов: {len(completed_orders)}\n"
        short_text += f"Отмененных заказов: {len(cancelled_orders)}\n"
        
        if message:
            await message.answer(text=short_text, reply_markup=markups.create(markup), parse_mode="HTML")
        else:
            await callback_query.message.edit_text(text=short_text, reply_markup=markups.create(markup), parse_mode="HTML") 