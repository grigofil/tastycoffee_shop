from aiogram import types
import models
import constants
from markups import markups
import asyncio


async def execute(callback_query: types.CallbackQuery, user: models.users.User, data: dict, message=None) -> None:
    try:
        cart_items_dict = await user.cart.items.dict

        if not cart_items_dict:
            if message:
                return await message.answer(constants.language.cart_empty)
            return await callback_query.message.edit_text(constants.language.cart_empty)
        
        text = constants.language.cart
        
        def changeCart_callback(item_id: int, state: int) -> str:
            return f'{{"r":"user","iid":{item_id},"s":{state},"d":"cart"}}changeCart'

        markup = []

        # Add fallback for missing currency symbol
        try:
            currency = constants.config["settings"]["currency_symbol"]
        except (KeyError, FileNotFoundError):
            currency = "₽"  # Default to ruble symbol
            print("Warning: Missing currency_symbol in config, using default")

        total_price = 0
        for item_id, amount in cart_items_dict.items():
            item = models.items.Item(item_id)
            item_name, category, weight, item_price, discounted_price, total_price = await asyncio.gather(
                item.name,
                item.category_name,
                item.weight,
                item.price,
                item.discounted_price,
                user.cart.total_price
            )
            display_price = discounted_price
            price_text = f"[{display_price}{currency}]"
            if display_price != item_price:
                price_text = f"[{display_price}{currency}]"
            markup.append((f"{price_text} {item_name} {category} {weight}г", f'{{"r":"user","rd":"cart","iid":{item.id}}}item'))
            markup += [(
                (constants.language.minus, changeCart_callback(item_id, 0)),
                (f"[{amount}] {amount*display_price}{currency}", "None"),
                (constants.language.plus, changeCart_callback(item_id, 1))
            )]

        payment_method, delivery_id = await asyncio.gather(
            user.cart.payment_method,
            user.cart.delivery_id
        )
        changePaymentMethod_callback = f"{constants.JSON_USER}cyclePaymentMethod"
        markup.append(
            (constants.language.payment_method, changePaymentMethod_callback) 
            if not payment_method.id else
            (payment_method["title"], changePaymentMethod_callback)
        )

        # Add better error handling for delivery config
        try:
            delivery_config = constants.config["delivery"]
            if delivery_config.get("enabled", False):
                markup.append((
                    constants.language.format_delivery(delivery_config.get("price", 0)) if delivery_id else constants.language.self_pickup,
                    f"{constants.JSON_USER}cycleDelivery"
                ))
        except (KeyError, AttributeError) as e:
            print(f"Warning: Error accessing delivery config: {e}")
            # Continue without delivery option

        markup.append(
            (constants.language.cart_total_price(total_price, currency), "None")
        )
        markup.append(
            (constants.language.clear_cart, f"{constants.JSON_USER}clearCart")
        )
        markup.append(
            (constants.language.cart_checkout, f"{constants.JSON_USER}checkout")
        )

        markup = markups.create(markup)

        if not message:
            return await callback_query.message.edit_text(
                text=text,
                reply_markup=markup
            )
        await message.answer(
            text=text,
            reply_markup=markup
        )

    except Exception as e:
        print(f"Error in cart callback: {e}")
        if message:
            return await message.answer("Произошла ошибка при загрузке корзины. Попробуйте позже.")
        return await callback_query.message.edit_text("Произошла ошибка при загрузке корзины. Попробуйте позже.")


