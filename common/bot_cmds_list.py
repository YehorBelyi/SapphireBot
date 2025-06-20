from aiogram.types import BotCommand

private = [
    BotCommand(command='help', description="Show special help menu"),
    BotCommand(command='start', description="Show start menu"),
    BotCommand(command='history', description="Show your order history"),
]

admin_commands = {
    "/add_employee": "Adds an administrator to the shop",
    "/add_manager": "Adds a manager to the shop",
}