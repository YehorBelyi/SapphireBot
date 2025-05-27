import asyncio
import os
import logging
from dotenv import load_dotenv
from middlewares.database import DataBaseSession

load_dotenv()

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import BotCommandScopeAllPrivateChats
from aiogram.enums import ParseMode
from database.engine import create_db, drop_db, session_maker

from handlers.user_private import user_private_router
from handlers.user_group import user_group_router
from handlers.admin_private import admin_router
from common.bot_cmds_list import private

# Added parsemode to format bot messages
bot = Bot(token=os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# dp.update.middleware(CounterMiddleware())

# Addomg admins for my bot
bot.my_admins_list = []

# Added all handlers from modules
dp.include_routers(user_private_router, user_group_router, admin_router)

async def on_startup(bot):
    run_param = False
    if run_param:
        await drop_db()

    # If old database wasn't dropped, new one won't be created, therefore data that exists there won't be modified
    # This is how method create_db() works
    await create_db()

async def on_shutdown(bot):
    print('Shutting down')

async def main() -> None:
    # Doing some actions automatically, f.e related with database, whenever launches or shutdowns
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Allowing all handlers to use databse middleware, so we can easily do actions with database anywhere
    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.delete_my_commands(scope=BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=private, scope=BotCommandScopeAllPrivateChats())
    # resolve_used_update_types - bot will process only those updates, which we use in the project
    # in particular: message, edited_message, callback_query
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting...")