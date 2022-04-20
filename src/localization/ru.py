admin_panel = "🔴 Админ панель"
faq = "ℹ️ FAQ"
profile = "📁 Профиль"
catalogue = "🗄️ Каталог"
cart = "🛒 Корзина"
support_menu = "☎ Меню тех. поддержки"

# Admin panel tabs
item_management = "📦 Управление товаром"
user_management = "🧍 Управление пользователями"
stats = "📈 Статистика"
settings = "⚙ Настройки"

# FAQ
contacts = "📞 Контакты"
refund_policy = "🎫 Политика возврата"

# Profile
my_orders = "📂 Мои заказы"
cancel_order = "❌ Отменить заказ"
restore_order = "✅ Восстановить заказ"
my_support_tickets = "🙋 Мои тикеты в тех. поддержку"
enable_notif = "🔔Включить оповещения о заказах"
disable_notif = "🔕Выключить оповещения о заказах"

# Catalogue / Item / Cart
search = "🔍 Найти"
add_to_cart = "🛒 Добавить в корзину"
not_in_stock = "❌ Нет в наличии"
cart_is_empty = "Корзина пуста."
pickup = "✅Самовывоз"
def delivery_on(price): return f"✅ Доставка - {price}руб."
def delivery_off(price): return f"❌ Доставка - {price}руб."
cart_checkout = "Оформить заказ"
clear_cart = "Очистить корзину"
processing = "Обрабатывается"
delivery = "Ожидает доставки"
done = "Готов"
cancelled = "Отменён"
def item(item):
    stock = "под заказ" if item.is_custom else f"{item.amount}"
    return f"{item.name}\n{item.price:.2f} руб.\nВ наличии: {stock}\n{item.description}"

# Item management
add_cat = "🛍️ Добавить категорию"
add_item = "🗃️ Добавить товар"
edit_cat = "✏️ Редактировать категорию"
edit_item = "✏️ Редактировать товар"
change_name = "📋 Изменить название"
change_image = "🖼️ Изменить изображение"
hide_image = "🙈 Скрыть изображение"
show_image = "🐵 Показать изображение"
change_desc = "📝 Изменить описание"
change_price = "🏷️ Изменить цену"
change_item_cat = "🛍️ Изменить категорию"
change_stock = "📦 Изменить кол-во"

# User management
user_profile = "📁Профиль пользователя"
notify_everyone = "🔔Оповещение всем пользователям"
orders = "📁 Заказы"
remove_manager_role = "👨‍💼 Убрать роль менеджера"
add_manager_role = "👨‍💼 Сделать менеджером"
remove_admin_role = "🔴 Убрать роль администратора"
add_admin_role = "🔴 Сделать администратором"
def change_order_status(status): return f"Изменить статус на \"{status}\""

# Shop stats
registration_stats = "👥Статистика регистраций"
order_stats = "📦Статистика заказов"
all_time = "За всё время"
monthly = "За последние 30 дней"
weekly = "За последние 7 дней"
daily = "За последние 24 часа"

# Shop settings
main_settings = "🛠️ Основные настройки"
item_settings = "🗃️ Настройки товаров"
additional_settings = "📖 Дополнительные настройки"
custom_commands = "📖 Команды"
add_command = "📝 Добавить команду"
clean_logs = "📖 Очистить логи"
clean_logs_text = "⚠️ Вы уверены, что хотите очистить логи? Они будут удалены без возможности восстановления!\n(Логи за сегодняшний день не будут удалены)"
backups = "💾 Резервное копирование"
update_backup = "🔄 Обновить резервную копию"
load_backup = "💿 Загрузить резервную копию"
clean_backups = "🧹 Очистка резервных копий"
system_settings = "💻 Система"
clean_images = "🗑️ Удалить неиспользуемые изображения"
clean_images_text = "⚠️ Вы уверены, что хотите удалить неспользуемые изображения? Они будут удалены без возможности восстановления!"
clean_database = "📚 Очистить базу данных"
clean_database_text = "⚠️ Вы уверены, что хотите очистить базу данных? Все данные будут удалены без возможности восстановления!"
reset_settings = "⚙️ Сбросить настройки"
resert_settings_text = "⚠️ Вы уверены, что хотите сбросить настройки? Все данные будут удалены без возможности восстановления!"
disable_item_image = "✅ Картинки товаров"
enable_item_image = "❌ Картинки товаров"
checkout_settings = "💳 Настройки оформления заказа"
stats_settings = "📈 Настройки статистики"
graph_color = "🌈 Цвет графика"
border_width = "🔲 Ширина обводки"
title_font_size = "ℹ️ Размер названия графика"
axis_font_size = "↔️Размер текста для осей"
tick_font_size = "🔢Размер текста для делений"
unavailable = "⛔️"
minus = "➖"
plus = "➕"
enable_sticker = "❌ Стикер в приветствии"
disable_sticker = "✅ Стикер в приветствии"
enable_phone_number = "❌ Номер телефона при заказе"
disable_phone_number = "✅ Номер телефона при заказе"
enable_delivery = "❌ Доставка"
disable_delivery = "✅ Доставка"
def delivery_price(price): return f"🚚 Стоимость доставки: {price}руб."
enable_captcha = "❌ CAPTCHA при заказе"
disable_captcha = "✅ CAPTCHA при заказе"
enable_debug = "❌ Режим отладки"
disable_debug = "✅ Режим отладки"

# Manager tab
view_order = "📂 Посмотреть заказ"

# Misc buttons
skip = "⏭ Пропустить"
back = "🔙 Назад"
confirm = "✅ Да"
deny = "❌ Нет"
error = "Произошла ошибка!"
or_press_back = "или нажмите на кнопку \"Назад\"."
hide = "🙈 Скрыть"
show = "🐵 Показать"
delete = "❌ Удалить"
reset = "❌ Сбросить"
no_permission = "У вас нет прав для выполнения данной команды!"
unknown_command = "Не могу понять команду :("
