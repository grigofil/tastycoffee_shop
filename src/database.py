import aiosqlite


async def fetch(query: str, *args) -> list:
    async with aiosqlite.connect("database.db") as db:
        if not args:
            # No arguments provided
            cursor = await db.execute(query)
        elif len(args) == 1:
            # Single argument case - SQLite expects (value,) for a single parameter query
            param = args[0]
            if isinstance(param, (list, tuple)):
                # Already a sequence, pass as is
                cursor = await db.execute(query, param)
            else:
                # Single value, make it a tuple with one element
                cursor = await db.execute(query, (param,))
        else:
            # Multiple arguments case
            cursor = await db.execute(query, args)
        
        await db.commit()
        result = await cursor.fetchall()
        return list(result) if result else []

