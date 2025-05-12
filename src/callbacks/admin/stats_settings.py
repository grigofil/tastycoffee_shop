from aiogram import types
import models
import constants
from markups import markups
import config


async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    if not data:
        data = {}
    
    param_to_change = data.get('param')
    action = data.get('action')
    
    # Get current settings or set defaults
    if "stats_settings" not in constants.config:
        constants.config.set("stats_settings", {
            "graph_color": "Blues",
            "border_width": 1.2,
            "title_font_size": 14,
            "axis_font_size": 12,
            "tick_font_size": 10
        })
    
    settings = constants.config["stats_settings"]
    
    # Handle parameter changes
    if param_to_change and action:
        if param_to_change == "graph_color":
            # Cycle through color maps
            color_maps = ["Blues", "Greens", "Reds", "Oranges", "Purples", "viridis", "plasma", "inferno"]
            current_index = color_maps.index(settings["graph_color"]) if settings["graph_color"] in color_maps else 0
            
            if action == "next":
                new_index = (current_index + 1) % len(color_maps)
            else:  # prev
                new_index = (current_index - 1) % len(color_maps)
            
            settings["graph_color"] = color_maps[new_index]
        else:
            # Handle numeric parameters
            numeric_params = {
                "border_width": {"min": 0.5, "max": 3.0, "step": 0.1},
                "title_font_size": {"min": 8, "max": 24, "step": 1},
                "axis_font_size": {"min": 6, "max": 20, "step": 1},
                "tick_font_size": {"min": 6, "max": 16, "step": 1}
            }
            
            if param_to_change in numeric_params:
                param_config = numeric_params[param_to_change]
                current_value = float(settings[param_to_change])
                
                if action == "inc":
                    new_value = min(current_value + param_config["step"], param_config["max"])
                else:  # dec
                    new_value = max(current_value - param_config["step"], param_config["min"])
                
                # Convert to int if it's a font size
                if "font_size" in param_to_change:
                    new_value = int(new_value)
                
                settings[param_to_change] = new_value
        
        # Save updated settings
        constants.config.set("stats_settings", settings)
    
    # Create message text
    text = constants.language.stats_settings + "\n\n"
    text += f"🌈 {constants.language.graph_color}: {settings['graph_color']}\n"
    text += f"🔲 {constants.language.border_width}: {settings['border_width']}\n"
    text += f"ℹ️ {constants.language.title_font_size}: {settings['title_font_size']}\n"
    text += f"↔️ {constants.language.axis_font_size}: {settings['axis_font_size']}\n"
    text += f"🔢 {constants.language.tick_font_size}: {settings['tick_font_size']}\n"
    
    # Create markup
    markup = []
    
    # Graph color
    markup.append((
        constants.language.graph_color,
        f'{{"r":"admin","param":"graph_color","action":"next"}}stats_settings'
    ))
    
    # Border width
    markup.extend([
        (f"{constants.language.border_width} {constants.language.minus}", 
         f'{{"r":"admin","param":"border_width","action":"dec"}}stats_settings'),
        (f"{constants.language.border_width} {constants.language.plus}", 
         f'{{"r":"admin","param":"border_width","action":"inc"}}stats_settings')
    ])
    
    # Title font size
    markup.extend([
        (f"{constants.language.title_font_size} {constants.language.minus}", 
         f'{{"r":"admin","param":"title_font_size","action":"dec"}}stats_settings'),
        (f"{constants.language.title_font_size} {constants.language.plus}", 
         f'{{"r":"admin","param":"title_font_size","action":"inc"}}stats_settings')
    ])
    
    # Axis font size
    markup.extend([
        (f"{constants.language.axis_font_size} {constants.language.minus}", 
         f'{{"r":"admin","param":"axis_font_size","action":"dec"}}stats_settings'),
        (f"{constants.language.axis_font_size} {constants.language.plus}", 
         f'{{"r":"admin","param":"axis_font_size","action":"inc"}}stats_settings')
    ])
    
    # Tick font size
    markup.extend([
        (f"{constants.language.tick_font_size} {constants.language.minus}", 
         f'{{"r":"admin","param":"tick_font_size","action":"dec"}}stats_settings'),
        (f"{constants.language.tick_font_size} {constants.language.plus}", 
         f'{{"r":"admin","param":"tick_font_size","action":"inc"}}stats_settings')
    ])
    
    # Back button
    markup.append((constants.language.back, f"{constants.JSON_ADMIN}settings"))
    
    # Send or edit message
    if message:
        await message.answer(text, reply_markup=markups.create(markup))
    else:
        await callback_query.message.edit_text(text, reply_markup=markups.create(markup)) 