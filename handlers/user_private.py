from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, or_f
from aiogram.utils.formatting import as_list, as_marked_section, Bold
from filters.chat_types import ChatTypeFilter

from keyboards.reply import generate_keyboard

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))

@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Welcome to Sapphire Shop",
                         reply_markup=generate_keyboard(
                             "Menu", "About", "Cart", "Order history", "Send number", "Payment methods",
                             placeholder="Choose an option below",
                             sizes=(2,2),
                             request_contact=4
                         ))

@user_private_router.message(or_f(Command("menu"), (F.text.lower() == "menu")))
async def echo(message: types.Message):
    await message.answer("Command menu")

@user_private_router.message(or_f(Command("about"), (F.text.lower() == "about")))
async def echo(message: types.Message):
    await message.answer("About our shop")

@user_private_router.message(or_f(Command("payment"), (F.text.lower() == "payment methods")))
async def echo(message: types.Message):
    text = as_marked_section(
        Bold("You can choose either:"),
        "Credit card",
        "After receiving product",
        "Cryptocurrency",
        marker="✅ "
    )
    await message.answer(text.as_html())

@user_private_router.message(F.contact)
async def contact(message: types.Message):
    await message.answer(str(message.contact))