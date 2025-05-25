from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command

user_private_router = Router()

@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("This was command named 'start'")

@user_private_router.message(Command("menu"))
async def echo(message: types.Message):
    await message.answer("Command menu")