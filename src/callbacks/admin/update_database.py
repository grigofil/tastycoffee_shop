from aiogram import types
import models
import constants
from markups import markups
import asyncio
import subprocess
import os
import sys

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    # Send initial message that process has started
    if message:
        msg = await message.answer("Начался процесс обновления базы данных, это может занять некоторое время...")
    else:
        msg = await callback_query.message.edit_text("Начался процесс обновления базы данных, это может занять некоторое время...")
    
    # Execute the data collection script
    try:
        # Run the script asynchronously
        process = await asyncio.create_subprocess_exec(
            sys.executable, 
            "src/utils/update_database.py", 
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            result_text = "База данных успешно обновлена!"
        else:
            error_msg = stderr.decode('utf-8')
            result_text = f"Произошла ошибка при обновлении базы данных: {error_msg}"
    
    except Exception as e:
        result_text = f"Произошла ошибка при обновлении базы данных: {str(e)}"
    
    markup = markups.create([(constants.language.back, f"{constants.JSON_ADMIN}adminPanel")])
    await msg.edit_text(result_text, reply_markup=markup) 