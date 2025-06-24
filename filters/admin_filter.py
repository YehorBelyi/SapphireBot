from aiogram.filters import Filter
from aiogram import Bot, types
from database.orm_query import orm_get_employees
from sqlalchemy.ext.asyncio import AsyncSession


class IsAdmin(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: types.Message, bot: Bot, session: AsyncSession) -> bool:
        bot.my_admins_list = {int(employee["user_id"]) for employee in await orm_get_employees(session)}
        return message.from_user.id in bot.my_admins_list