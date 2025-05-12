import json
import database
from typing import Any

import constants
import datetime

class Order:
    def __init__(self, id: int) -> None:
        self.id = id

    async def __query(self, field: str) -> Any:
        return (await database.fetch(f"SELECT {field} FROM orders WHERE id = ?", self.id))[0][0]

    async def __update(self, field: str, value: Any) -> None:
        await database.fetch(f"UPDATE orders SET {field} = ? WHERE id = ?", value, self.id)

    @property
    def database_table(self) -> str:
        return """CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            username TEXT,
            items TEXT NOT NULL,
            adress TEXT,
            phone_number TEXT,
            email TEXT,
            comment TEXT,
            status INTEGER NOT NULL DEFAULT 0,
            date_created TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )"""

    @property
    async def user_id(self) -> int:
        return await self.__query("user_id")
    
    

    # items is a json string
        # items: [
        #   {
        #       "id": 1,
        #       "amount": 2
        #       "title": "title",
        #       "price": 100 # price per item
        #   }
        # ]
        # payment_method_id: 1
        # delivery_id: 1
        # delivery_price: 100

    @property
    async def __items_raw(self) -> str:
        return await self.__query("items")

    @property
    async def __items_json(self) -> dict:
        return json.loads(await self.__items_raw)

    @property
    async def items(self) -> list["__Item"]:
        return [self.__Item(item) for item in await self.__items_json]

    class __Item:
        def __init__(self, item_raw: dict) -> None:
            self.__item_raw = item_raw
        
        def __repr__(self) -> str:
            return str(self.__item_raw)

        def __str__(self) -> str:
            return str(self.__item_raw)

        @property
        def dict(self) -> dict:
            # Если __item_raw уже словарь, просто вернуть его
            if isinstance(self.__item_raw, dict):
                return self.__item_raw
            # Иначе попробовать разобрать как JSON
            return json.loads(self.__item_raw)

        @property
        def id(self) -> int:
            return int(self.dict["id"])

        @property
        def amount(self) -> int:
            return int(self.dict["amount"])

        @property
        def title(self) -> str:
            return self.dict["title"]

        @property
        def price(self) -> int:
            return int(self.dict["price"])

    @property
    async def payment_method_id(self) -> int:
        return int((await self.__items_json)["payment_method_id"])

    @property
    async def delivery_id(self) -> int:
        return int((await self.__items_json)["delivery_id"])

    @property
    async def delivery_price(self) -> int:
        return int((await self.__items_json)["delivery_price"])

    @property
    async def adress(self) -> str | None:
        return await self.__query("adress")

    @property
    async def phone_number(self) -> str | None:
        return await self.__query("phone_number")

    @property
    async def email(self) -> str | None:
        return await self.__query("email")

    @property
    async def comment(self) -> str | None:
        return await self.__query("comment")

    @property
    async def status(self) -> int:
        return await self.__query("status")
    async def set_status(self, status: int) -> None:
        await self.__update("status", status)

    @property
    async def date_created_raw(self) -> str:
        return await self.__query("date_created")
    @property
    async def date_created(self) -> datetime.datetime:
        date_str = await self.date_created_raw
        try:
            # Try parsing with the standard format first
            return datetime.datetime.strptime(date_str, constants.TIME_FORMAT)
        except ValueError:
            # If that fails, try parsing with microseconds
            try:
                # Split the string to handle microseconds separately
                main_part = date_str.split('.')[0]
                return datetime.datetime.strptime(main_part, constants.TIME_FORMAT)
            except Exception as e:
                # If all parsing fails, return current time and log error
                print(f"Error parsing date: {date_str} - {str(e)}")
                return datetime.datetime.now()

    @property
    async def username(self) -> str | None:
        return await self.__query("username")

async def get_orders_by_status(status: int) -> list[Order]:
    return [Order(order_id) for order_id in (await database.fetch("SELECT id FROM orders WHERE status = ?", status))]

async def create(
    user_id: int,
    items_json: str,
    date_created: datetime.datetime | None,
    adress: str | None = None,
    phone_number: str | None = None,
    email: str | None = None,
    comment: str | None = None,
    username: str | None = None,
) -> Order:
    # Format date if provided, otherwise use current time
    if date_created is None:
        date_created = datetime.datetime.now()
    
    # Format date without microseconds to ensure consistent format
    date_str = date_created.strftime(constants.TIME_FORMAT)
    
    # Put all parameters in a tuple
    params = (user_id, username, items_json, adress, phone_number, email, comment, date_str)
    
    await database.fetch(
        "INSERT INTO orders (user_id, username, items, adress, phone_number, email, comment, date_created) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        params
    )
    
    # Get the last inserted order ID
    result = await database.fetch("SELECT id FROM orders ORDER BY id DESC LIMIT 1")
    if result and len(result) > 0:
        return Order(result[0][0])
    else:
        raise ValueError("Failed to create order")


