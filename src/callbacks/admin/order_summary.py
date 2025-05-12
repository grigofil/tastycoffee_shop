from aiogram import types
import models
import constants
from markups import markups
import asyncio
import matplotlib.pyplot as plt
from io import BytesIO
import numpy as np
from callbacks.admin.stats import get_order_items_summary
import localization.ru as language

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    # Получаем сводку по всем товарам в текущих заказах
    items_summary = await get_order_items_summary()
    
    # Формируем текст отчета
    text = f"{language.order_summary}\n\n"
    
    if not items_summary:
        text += language.no_active_orders
    else:
        # Вычисляем общую сумму и количество товаров
        total_items = sum(item[1]["total_amount"] for item in items_summary)
        total_value = sum(item[1]["total_amount"] * item[1]["price"] for item in items_summary)
        
        text += f"{language.total_active_items}: {len(items_summary)}\n"
        text += f"{language.total_item_count}: {total_items}\n"
        text += f"{language.total_cost}: {total_value:.2f} {constants.config['settings']['currency_symbol']}\n\n"
        
        # Добавляем в отчет топ-10 товаров по количеству
        text += f"🔝 {language.popular_items}:\n"
        for i, (item_id, item_data) in enumerate(items_summary[:10], 1):
            total_price = item_data["total_amount"] * item_data["price"]
            category_name = item_data.get("category", "")
            text += f"{i}. {item_data['title']} ({category_name}) - {item_data['total_amount']} шт. ({total_price:.2f} {constants.config['settings']['currency_symbol']})\n"
        
        # Создаем график распределения товаров по категориям, если есть данные
        if len(items_summary) > 1:
            # Создаем словарь для подсчета количества товаров по категориям
            category_counts = {}
            for item_id, item_data in items_summary:
                category_name = item_data.get("category", "Без категории")
                if category_name not in category_counts:
                    category_counts[category_name] = 0
                category_counts[category_name] += item_data["total_amount"]
            
            # Сортируем категории по количеству товаров
            sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
            
            # Отбираем топ-5 категорий, остальные объединяем в "Другие"
            top_categories = sorted_categories[:5]
            other_categories = sorted_categories[5:]
            
            if other_categories:
                other_sum = sum(count for _, count in other_categories)
                top_categories.append(("Другие", other_sum))
            
            # Данные для построения графика
            labels = [cat for cat, _ in top_categories]
            sizes = [count for _, count in top_categories]
            
            # Создание графика
            plt.figure(figsize=(8, 6))
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            plt.title('Распределение товаров по категориям')
            
            # Сохраняем график в буфер
            chart_buffer = BytesIO()
            plt.savefig(chart_buffer, format='png')
            chart_buffer.seek(0)
            plt.close()
            
            # Отправляем сообщение с графиком
            await callback_query.message.delete()
            await callback_query.message.answer_photo(
                photo=types.InputFile(chart_buffer, filename='category_distribution.png'),
                caption=text,
                reply_markup=markups.create([
                    (constants.language.full_statistics, f"{constants.JSON_ADMIN}full_order_summary"),
                    (constants.language.back, f"{constants.JSON_ADMIN}stats")
                ])
            )
            return
    
    # Если нет данных для графика или всего один товар, отправляем только текст
    await callback_query.message.edit_text(
        text=text,
        reply_markup=markups.create([
            (constants.language.full_statistics, f"{constants.JSON_ADMIN}full_order_summary"),
            (constants.language.back, f"{constants.JSON_ADMIN}stats")
        ])
    )

async def generate_items_chart(items_summary):
    """Создает график с распределением товаров по количеству"""
    # Подготовка данных для графика
    labels = [item[1]["title"] if len(item[1]["title"]) <= 20 else item[1]["title"][:18] + "..." for item in items_summary]
    amounts = [item[1]["total_amount"] for item in items_summary]
    
    # Создаем горизонтальную гистограмму
    fig, ax = plt.subplots(figsize=(10, 8))
    y_pos = np.arange(len(labels))
    
    # Добавляем русскую локализацию для шрифтов
    plt.rcParams['font.family'] = 'DejaVu Sans'
    
    bars = ax.barh(y_pos, amounts, align='center')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()  # Самое большое значение сверху
    ax.set_xlabel(language.items_count)
    ax.set_title(language.items_distribution)
    
    # Добавляем числа в конце каждого столбца
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width + 0.3, bar.get_y() + bar.get_height()/2, 
                f'{width}', ha='left', va='center')
    
    plt.tight_layout()
    
    # Сохраняем график в буфер
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)
    plt.close(fig)
    
    return buffer 