from aiogram import types
import models
import constants
from markups import markups
from callbacks.admin.stats import get_order_items_summary
import localization.ru as language
import asyncio

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    # Получение номера страницы из данных
    page = int(data.get("page", 1))
    
    # Получаем сводку по всем товарам в текущих заказах
    items_summary = await get_order_items_summary()
    
    if not items_summary:
        text = language.no_active_orders
        markup = markups.create([(constants.language.back, f"{constants.JSON_ADMIN}stats")])
        await callback_query.message.edit_text(text=text, reply_markup=markup)
        return
    
    # Настройки пагинации
    items_per_page = 15
    total_pages = (len(items_summary) + items_per_page - 1) // items_per_page
    
    # Ограничиваем страницу в пределах допустимого диапазона
    page = max(1, min(page, total_pages))
    
    # Расчет индексов для текущей страницы
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(items_summary))
    
    # Формируем текст отчета
    text = f"{language.full_order_summary} ({language.page} {page}/{total_pages})\n\n"
    
    # Вычисляем общую сумму и количество товаров
    total_items = sum(item[1]["total_amount"] for item in items_summary)
    total_value = sum(item[1]["total_amount"] * item[1]["price"] for item in items_summary)
    
    text += f"{language.total_active_items}: {len(items_summary)}\n"
    text += f"{language.total_item_count}: {total_items}\n"
    text += f"{language.total_cost}: {total_value:.2f} {constants.config['settings']['currency_symbol']}\n\n"
    
    # Выводим товары для текущей страницы
    for i, (item_id, item_data) in enumerate(items_summary[start_idx:end_idx], start_idx + 1):
        total_price = item_data["total_amount"] * item_data["price"]
        category_name = item_data.get("category", "")
        text += f"{i}. {item_data['title']} ({category_name}) - {item_data['total_amount']} шт. ({total_price:.2f} {constants.config['settings']['currency_symbol']})\n"
    
    # Кнопки навигации
    nav_buttons = []
    
    if total_pages > 1:
        if page > 1:
            nav_buttons.append((language.previous_page, f'{{"r":"admin","page":{page-1}}}full_order_summary'))
        if page < total_pages:
            nav_buttons.append((language.next_page, f'{{"r":"admin","page":{page+1}}}full_order_summary'))
    
    nav_buttons.append((language.order_summary, f"{constants.JSON_ADMIN}order_summary"))
    nav_buttons.append((constants.language.back, f"{constants.JSON_ADMIN}stats"))
    
    markup = markups.create(nav_buttons)
    
    await callback_query.message.edit_text(text=text, reply_markup=markup) 