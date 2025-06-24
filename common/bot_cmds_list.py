from aiogram.types import BotCommand

private = [
    BotCommand(command='start', description="Show start menu"),
    BotCommand(command='history', description="Show your order history"),
]

admin_commands = {
    "/add_employee": "Adds an employee to the shop",
    "/add_product": "Adds a product to the shop",
    "/all_products":"Shows a list of all products",
    "/manage_banners" :"Allows you to add/edit banners"
}