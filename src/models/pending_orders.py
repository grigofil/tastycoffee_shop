import json
import datetime
import database
import models
import constants

class PendingOrdersPool:
    def __init__(self) -> None:
        pass
    
    @property
    def database_table(self) -> str:
        return """CREATE TABLE IF NOT EXISTS pending_orders (
            id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            date_added TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            FOREIGN KEY (order_id) REFERENCES orders (id)
        )"""
    
    @staticmethod
    async def get_all_pending_orders():
        """Get all pending orders in the pool"""
        result = await database.fetch(
            "SELECT order_id FROM pending_orders WHERE status = 'pending' ORDER BY date_added"
        )
        return [models.orders.Order(row[0]) for row in result] if result else []
    
    @staticmethod
    async def get_pending_orders_count():
        """Get count of pending orders"""
        result = await database.fetch(
            "SELECT COUNT(*) FROM pending_orders WHERE status = 'pending'"
        )
        return result[0][0] if result else 0
    
    @staticmethod
    async def add_order_to_pool(order_id: int):
        """Add an order to the pending pool"""
        date_str = datetime.datetime.now().strftime(constants.TIME_FORMAT)
        await database.fetch(
            "INSERT INTO pending_orders (order_id, date_added) VALUES (?, ?)",
            (order_id, date_str)
        )
    
    @staticmethod
    async def mark_order_as_processed(order_id: int):
        """Mark an order as processed in the pool"""
        await database.fetch(
            "UPDATE pending_orders SET status = 'processed' WHERE order_id = ?",
            order_id
        )
    
    @staticmethod
    async def get_statistics():
        """Get statistics about orders in the pool"""
        # Count of orders by status
        status_counts = await database.fetch(
            "SELECT status, COUNT(*) FROM pending_orders GROUP BY status"
        )
        
        # Total items ordered (requires joining with orders table)
        total_items = await database.fetch(
            """
            SELECT SUM(json_array_length(o.items)) 
            FROM pending_orders p
            JOIN orders o ON p.order_id = o.id
            WHERE p.status = 'pending'
            """
        )
        
        return {
            "status_counts": {row[0]: row[1] for row in status_counts} if status_counts else {},
            "total_pending_items": total_items[0][0] if total_items and total_items[0][0] is not None else 0
        } 