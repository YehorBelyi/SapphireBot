import asyncio
import os
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import BotCommandScopeAllPrivateChats
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from handlers.user_private import user_private_router
from handlers.user_group import user_group_router
from handlers.admin_private import admin_router
from common.bot_cmds_list import private
from middlewares.database import CounterMiddleware

load_dotenv()

ALLOWED_UPDATES = ['message, edited_message']

# Added parsemode to format bot messages
bot = Bot(token=os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# dp.update.middleware(CounterMiddleware())

# Addomg admins for my bot
bot.my_admins_list = []

# Added all handlers from modules
dp.include_routers(user_private_router, user_group_router, admin_router)

async def main() -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.delete_my_commands(scope=BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=private, scope=BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting...")