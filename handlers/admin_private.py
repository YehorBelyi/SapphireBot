from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from filters.chat_types import ChatTypeFilter
from filters.admin_filter import IsAdmin
from keyboards.reply import generate_keyboard

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

ADMIN_KB = generate_keyboard(
    "Add product", "Edit product", "Delete product", "Doing smth here",
    placeholder="Choose an action",
    sizes=(2, 1, 1)
)

@admin_router.message(Command("admin"))
async def admin_features(message: types.Message):
    await message.answer("What's next?", reply_markup=ADMIN_KB)