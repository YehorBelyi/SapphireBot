import dotenv
import os
from aiogram import types, Bot
from aiogram.utils.formatting import Underline
from common.view import categories, roles

ADMIN_CHANNEL = os.getenv("ADMIN_CHANNEL")

async def log_product_added(data: dict, bot: Bot):
    product_category = categories[int(data["category"])-1]
    await Bot.send_message(self=bot,chat_id=ADMIN_CHANNEL, text=f'✅ <b>New product has been added to the shop!</b>'
                                                                f'\n\n<i>Name:</i> {data["name"]}'
                                                                f'\n️️<i>Description:</i> {data["desc"]}'
                                                                f'\n<i>Price:</i> {data["price"]}'
                                                                f'\n<i>Category:</i> {product_category}')

async def log_product_edited(data: dict, bot: Bot):
    product_category = categories[int(data["category"])-1]
    await Bot.send_message(self=bot,chat_id=ADMIN_CHANNEL, text=f'📝 <b>Product has been edited!</b>'
                                                                f'\n\n<i>Name:</i> {data["name"]}'
                                                                f'\n️️<i>Description:</i> {data["desc"]}'
                                                                f'\n<i>Price:</i> {data["price"]}'
                                                                f'\n<i>Category:</i> {product_category}')

async def log_product_deleted(product_id:str, bot: Bot):
    await Bot.send_message(self=bot,chat_id=ADMIN_CHANNEL, text=f'❌ <b>Product with ID: {product_id} has been deleted!</b>')

async def log_new_order_notification(user_orders: list, user_id:int, bot: Bot):
    str = f"🟧 <b>New order from ID:{user_id}</b>\n"
    for index, order in enumerate(user_orders, start=1):
        str += f"\n{index}) {order["name"]} x {order["quantity"]} item(s)"
    await Bot.send_message(self=bot, chat_id=ADMIN_CHANNEL, text=str)

async def log_new_employee(data: dict, bot: Bot):
    employee_role = roles[int(data["role_id"])-1]
    await Bot.send_message(self=bot, chat_id=ADMIN_CHANNEL, text=f'👤 <b>New employee has been added! Welcome!</b>'
                                                                f'\n\n<i>First name:</i> {data["first_name"]}'
                                                                f'\n️️<i>Last name:</i> {data["last_name"]}'
                                                                f'\n<i>Phone:</i> {data["phone"]}'
                                                                f'\n<i>Role:</i> {employee_role}')