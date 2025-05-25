import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import BotCommandScopeAllPrivateChats
from dotenv import load_dotenv

from handlers.user_private import user_private_router
from common.bot_cmds_list import private

load_dotenv()

ALLOWED_UPDATES = ['message, edited_message']

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

dp.include_router(user_private_router)

async def main() -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.delete_my_commands(scope=BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=private, scope=BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)

if __name__ == '__main__':
    asyncio.run(main())