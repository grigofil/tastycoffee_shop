import json
import datetime
import database
import constants

class CoffeeBeansOrder:
    def __init__(self) -> None:
        pass

    @property
    def database_table(self) -> str:
        return """CREATE TABLE IF NOT EXISTS coffee_beans_orders (
            id INTEGER PRIMARY KEY,
            total_weight REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'collecting',
            date_created TEXT NOT NULL,
            date_confirmed TEXT,
            payment_info TEXT
        )"""
    
    @staticmethod
    async def get_current_order():
        result = await database.fetch(
            "SELECT id FROM coffee_beans_orders WHERE status = 'collecting' ORDER BY date_created DESC LIMIT 1"
        )
        if not result:
            # Create new collecting order
            order_id = await database.fetch(
                "INSERT INTO coffee_beans_orders (date_created) VALUES (?)",
                datetime.datetime.now().strftime(constants.TIME_FORMAT)
            )
            return CoffeeBeansOrder.get_by_id(order_id)
        return CoffeeBeansOrder.get_by_id(result[0][0])

    @staticmethod
    def get_by_id(order_id: int):
        order = CoffeeBeansOrder()
        order.id = order_id
        return order

    async def get_total_weight(self) -> float:
        result = await database.fetch(
            "SELECT total_weight FROM coffee_beans_orders WHERE id = ?",
            self.id
        )
        return result[0][0] if result else 0

    async def add_weight(self, weight: float) -> None:
        current_weight = await self.get_total_weight()
        await database.fetch(
            "UPDATE coffee_beans_orders SET total_weight = ? WHERE id = ?",
            current_weight + weight,
            self.id
        )

    async def get_status(self) -> str:
        result = await database.fetch(
            "SELECT status FROM coffee_beans_orders WHERE id = ?",
            self.id
        )
        return result[0][0] if result else 'collecting'

    async def set_status(self, status: str) -> None:
        await database.fetch(
            "UPDATE coffee_beans_orders SET status = ? WHERE id = ?",
            status,
            self.id
        )

    async def confirm_by_admin(self) -> None:
        await self.set_status('pending_user_confirmation')
        await database.fetch(
            "UPDATE coffee_beans_orders SET date_confirmed = ? WHERE id = ?",
            datetime.datetime.now().strftime(constants.TIME_FORMAT),
            self.id
        )

    async def set_payment_info(self, info: str) -> None:
        await database.fetch(
            "UPDATE coffee_beans_orders SET payment_info = ? WHERE id = ?",
            info,
            self.id
        ) 