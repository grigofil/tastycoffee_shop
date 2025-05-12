import os
import json
from typing import Any

filename = "config.json"
class Config:
    def __init__(self):
        self.__cached_data = None
        
    def __repr__(self):
        return str(self.__data)

    def __iter__(self):
        # Return an iterator for the dictionary keys
        return iter(self.__data)

    def __getitem__(self, item):
        try:
            return self.__data[item]
        except KeyError as e:
            print(f"Failed to access config key: {item}")
            print(f"Available keys: {list(self.__data.keys())}")
            raise

    def __str__(self) -> str:
        return self.__raw 

    @property
    def __raw(self) -> str:
        with open(filename, "r") as f:
            return f.read()

    @property
    def __data(self):
        if getattr(self, '__cached_data', None) is None:
            try:
                self.__cached_data = json.loads(self.__raw)
            except (FileNotFoundError, json.JSONDecodeError):
                self.init()
                with open(filename, "r") as f:
                    self.__cached_data = json.loads(f.read())
        return self.__cached_data

    def set(self, param: str | tuple[str, str], value: Any) -> None:
        modified_data = self.__data

        if isinstance(param, tuple):
            modified_data[param[0]][param[1]] = value
        else:
            modified_data[param] = value

        backup_filename = f"{filename}.bak"
        if os.path.exists(backup_filename):
            os.remove(backup_filename)
        with open(backup_filename, "w") as f:
            json.dump(modified_data, f, indent=2)        
        os.remove(filename)
        with open(filename, "w") as f:
            json.dump(modified_data, f, indent=2)
        
        # Update cache
        self.__cached_data = modified_data

    def init(self) -> None:
        data = {
            "settings": {
                "language": "ru",
                "currency": "RUB",
                "currency_symbol": "₽",
                "debug": True,
            },
            "delivery": {
                "price": 0,
                "enabled": False,
            },
            "checkout": {
                "adress": True,
                "phone": True,
                "email": True,
                "captcha": True,
            },
            "payment_methods": {
                "cash": {
                    "title": "Наличными",
                    "enabled": True,
                },
                "manager": {
                    "title": "Оплата после связи с менеджером",
                    "enabled": True,
                },
                "telegram_api": {
                    "title": "Оплата через Telegram",
                    "enabled": False,
                },
            },
            "info": {
                "greeting": "Приветствуем в боте по заказу кофе из TastyCoffee! \nЗаказ делается по достижению минимального объема для заказа - 25 кг, по достижению нужного объема придет уведомление.",
                "contacts": "Телефон: +7 (919) 919-071-63-17\nАдрес: г. Москва, Кутузовский пр., 32 к3, башня Б",
                "refund_policy": "Политика возврата - ее нет",
                "item_template": "Название: %n за %w г\nКатегория: %c\nЦена: %p\n\nОписание: %d",
            },
            "coffee_beans": {
                "min_order_weight": 25.0
            }
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        self.__cached_data = data

config = Config()


