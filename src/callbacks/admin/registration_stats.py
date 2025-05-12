from aiogram import types
import models
import constants
from markups import markups
import datetime
import asyncio
import matplotlib.pyplot as plt
from io import BytesIO
import localization.ru as language
from callbacks.admin.stats import get_users_stats, generate_pie_chart


async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    period = data.get('period', 'all')
    
    if period == 'all':
        # Show period selection menu
        text = constants.language.registration_stats
        markup = markups.create([
            (constants.language.all_time, f'{{"r":"admin","period":"all_time"}}registration_stats'),
            (constants.language.monthly, f'{{"r":"admin","period":"monthly"}}registration_stats'),
            (constants.language.weekly, f'{{"r":"admin","period":"weekly"}}registration_stats'),
            (constants.language.daily, f'{{"r":"admin","period":"daily"}}registration_stats'),
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
        title = constants.language.weekly
    elif period == 'daily':
        period_key = 'daily'
        title = constants.language.daily
    
    # Fetch statistics
    user_stats = await get_users_stats(period_key)
    
    # Basic statistics
    total_users = len(user_stats)
    
    # Prepare text message
    text = f"{constants.language.registration_stats} ({title}):\n\n"
    text += f"👥 {language.total_users}: {total_users}\n"
    
    # Time-based distribution analysis if we have enough data
    if total_users > 0 and period != 'daily':
        # Generate daily registration counts for time series
        registration_dates = []
        for u in user_stats:
            registration_dates.append(await u.date_created)
        
        # Group by date
        date_counts = {}
        for date in registration_dates:
            date_key = date.strftime('%Y-%m-%d')
            date_counts[date_key] = date_counts.get(date_key, 0) + 1
        
        if len(date_counts) > 1:
            # Create a chart - we'll use a pie chart for user roles and line chart for registrations over time
            # For this example, let's check for admin/manager roles
            admin_count = 0
            manager_count = 0
            regular_count = 0
            
            for u in user_stats:
                is_admin, is_manager = await asyncio.gather(u.is_admin, u.is_manager)
                if is_admin:
                    admin_count += 1
                elif is_manager:
                    manager_count += 1
                else:
                    regular_count += 1
            
            # Generate user roles pie chart if we have users with different roles
            if admin_count > 0 or manager_count > 0:
                labels = []
                sizes = []
                
                if regular_count > 0:
                    labels.append(language.role_regular_user)
                    sizes.append(regular_count)
                if manager_count > 0:
                    labels.append(language.role_manager)
                    sizes.append(manager_count)
                if admin_count > 0:
                    labels.append(language.role_admin)
                    sizes.append(admin_count)
                
                chart_title = f"{language.user_roles_distribution} ({title})"
                chart_buffer = await generate_pie_chart(sizes, labels, chart_title)
                
                # Send the chart as a photo
                await callback_query.message.delete()
                await callback_query.message.answer_photo(
                    types.InputFile(chart_buffer, filename='user_stats.png'),
                    caption=text,
                    reply_markup=markups.create([
                        (constants.language.back, f"{constants.JSON_ADMIN}registration_stats")
                    ])
                )
                return
    
    # If we don't have enough data for a chart or it's a daily view, just show text stats
    await callback_query.message.edit_text(
        text=text,
        reply_markup=markups.create([
            (constants.language.back, f"{constants.JSON_ADMIN}registration_stats")
        ])
    ) 