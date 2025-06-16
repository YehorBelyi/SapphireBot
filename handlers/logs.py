import dotenv
import os
from aiogram import types, Bot
from aiogram.utils.formatting import Underline

ADMIN_CHANNEL = os.getenv("ADMIN_CHANNEL")

async def log_product_added(data: dict, bot: Bot):
    await Bot.send_message(self=bot,chat_id=ADMIN_CHANNEL, text=f'✅ <b>New product has been added to the shop!</b> ✅'
                                                                f'\n\n <i>Name:</i> {data["name"]}'
                                                                f'\n️️<i>Description:</i> {data["desc"]}'
                                                                f'\n<i>Price:</i> {data["price"]}'
                                                                f'\n<i>Category:</i> {data["category"]}')