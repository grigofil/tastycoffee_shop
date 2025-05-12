from aiogram import types
import models
import constants
from markups import markups
from localization import ru as language

ITEMS_PER_PAGE = 8  # Number of categories per page

async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    page = int(data.get('page', 1))
    categories = await models.categories.get_categories()
    
    # Calculate pagination
    total_pages = (len(categories) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    start_idx = (page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    
    # Create markup for current page
    markup = [
        (f"[{category.id}] {await category.name}", f'{{"r":"admin","cid":{category.id}}}editCategory')
        for category in categories[start_idx:end_idx]
    ]
    
    # Add navigation buttons if needed
    if total_pages > 1:
        if page > 1:
            markup.append((language.previous_page, f'{{"r":"admin","page":{page-1}}}editCategories'))
        if page < total_pages:
            markup.append((language.next_page, f'{{"r":"admin","page":{page+1}}}editCategories'))
    
    markup.append((language.back, f"{constants.JSON_ADMIN}categories"))

    await callback_query.message.edit_text(
        text=f"{language.edit_category}\n\n{language.page} {page}/{total_pages}",
        reply_markup=markups.create(markup)
    )

