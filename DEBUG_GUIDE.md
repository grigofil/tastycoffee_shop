# 🤖 Руководство по отладке Telegram бота

## ✅ Исправленные проблемы

### 1. Проблема с импортами
**Проблема:** Модули не могли найти друг друга из-за неправильных путей импорта.

**Решение:** Добавлен код в `src/__init__.py` для автоматического добавления папки `src` в Python path:
```python
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
```

### 2. Создан файл requirements.txt
Создан файл `requirements.txt` со всеми необходимыми зависимостями:
- aiogram==2.23.1
- aiohttp==3.8.3
- aiosqlite==0.17.0
- python-dotenv==0.21.0
- matplotlib==3.6.2
- и другие...

## 🚀 Как запустить бота

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка токена
Создайте файл `.env` в корне проекта:
```env
TOKEN=YOUR_BOT_TOKEN_HERE
```

Или установите переменную окружения:
```bash
# Windows
set TOKEN=YOUR_BOT_TOKEN_HERE

# Linux/Mac
export TOKEN=YOUR_BOT_TOKEN_HERE
```

### 3. Запуск бота
```bash
python src/__init__.py
```

## 🔧 Тестирование

### Запуск тестового скрипта
```bash
python test_bot.py
```

Этот скрипт проверит:
- ✅ Импорты всех модулей
- ✅ Конфигурацию
- ✅ Подключение к базе данных

### Простой тест
```bash
python simple_test.py
```

## 📁 Структура проекта

```
tastycoffee_shop/
├── src/                    # Основной код
│   ├── __init__.py        # Главный файл бота
│   ├── config.py          # Конфигурация
│   ├── database.py        # Работа с БД
│   ├── constants.py       # Константы
│   ├── models/            # Модели данных
│   ├── callbacks/         # Обработчики
│   └── ...
├── config.json           # Настройки бота
├── requirements.txt      # Зависимости
├── test_bot.py          # Тестовый скрипт
└── DEBUG_GUIDE.md       # Это руководство
```

## ⚠️ Возможные проблемы

### 1. "No token found!"
**Решение:** Убедитесь, что установлена переменная окружения TOKEN или создан файл .env

### 2. "ModuleNotFoundError"
**Решение:** Убедитесь, что все зависимости установлены:
```bash
pip install -r requirements.txt
```

### 3. "Database not found"
**Решение:** Бот автоматически создаст базу данных при первом запуске

### 4. Проблемы с PowerShell
Если команды не выполняются в PowerShell, попробуйте:
```bash
cmd /c "python src/__init__.py"
```

## 🎯 Следующие шаги

1. Получите токен бота от @BotFather в Telegram
2. Установите токен в переменную окружения или файл .env
3. Запустите бота: `python src/__init__.py`
4. Протестируйте бота, отправив команду /start

## 📞 Поддержка

Если у вас возникли проблемы:
1. Проверьте, что все зависимости установлены
2. Убедитесь, что токен бота корректный
3. Запустите тестовый скрипт для диагностики
4. Проверьте логи на наличие ошибок
