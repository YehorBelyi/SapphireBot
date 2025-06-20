from aiogram import F, Router, types, Bot
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from common.bot_cmds_list import admin_commands
from database.orm_query import orm_add_product, orm_get_products, orm_get_product, orm_delete_product, \
    orm_update_product, orm_get_categories, orm_get_page_description, orm_update_banner_image, orm_get_roles, \
    orm_add_employee

from filters.chat_types import ChatTypeFilter
from filters.admin_filter import IsAdmin
from handlers.logs import log_product_added, log_product_edited, log_product_deleted, log_new_employee
from keyboards.inline import get_callback_btns
from keyboards.reply import generate_keyboard
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import session

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

ADMIN_KB = generate_keyboard(
    "Add product", "All products", "Add/Edit banner",
    placeholder="Choose an action",
    sizes=(2,),
)

# Storing all steps when adding a product
class AddProduct(StatesGroup):
    name = State()
    desc = State()
    category = State()
    price = State()
    image = State()

    product_to_edit = None

    texts = {
        'AddProduct:name': 'Type name of the product again:',
        'AddProduct:desc': 'Type description of the product again:',
        'AddProduct:price': 'Type price of the product again:',
        'AddProduct:image': 'Attach image of the product again:',
    }

class AddEmployee(StatesGroup):
    user_id = State()
    first_name = State()
    last_name = State()
    phone = State()
    role_id = State()

    employee_to_edit = None

@admin_router.message(Command("admin"))
async def admin_features(message: types.Message):
    await message.answer("What's next?", reply_markup=ADMIN_KB)

# FSM for adding products to databse
# StateFilter(None) means that when admin is going to add new product, he won't have any active states at the moment
@admin_router.message(StateFilter(None), F.text == "Add product")
async def add_product(message: types.Message, state: FSMContext):
    await message.answer("Type name of the product:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddProduct.name)

# StateFilter('*') means state filter will work for any active state
@admin_router.message(StateFilter('*'), Command("cancel"))
@admin_router.message(StateFilter('*'), F.text.casefold() == "cancel")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    if AddProduct.product_to_edit:
        AddProduct.product_to_edit = None

    await state.clear()
    await message.answer("The process of adding a product was canceled", reply_markup=ADMIN_KB)

@admin_router.message(StateFilter('*'), Command("back"))
@admin_router.message(StateFilter('*'), F.text.casefold() == "back")
async def go_back_handler(message: types.Message, state: FSMContext) -> None:

    current_state = await state.get_state()
    if current_state == AddProduct.name:
        await message.answer("This is first step of adding a product. Type '/cancel' to abort the process")
        return

    previous = None
    for step in AddProduct.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f"You reverted to previous step\n{AddProduct.texts[previous.state]}")
            return
        previous = step

@admin_router.message(AddProduct.name, or_f(F.text, F.text == "."))
async def add_name(message: types.Message, state: FSMContext):
    if message.text == ".":
        await state.update_data(name=AddProduct.product_to_edit["name"])
    else:
        if len(message.text) >= 100:
            await message.answer("Name length of the product can't be greater than 100 characters!")
            return
        await state.update_data(name=message.text)

    await message.answer("Type desc of the product")
    await state.set_state(AddProduct.desc)

@admin_router.message(AddProduct.desc, F.text)
async def add_desc(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == ".":
        await state.update_data(desc=AddProduct.product_to_edit["description"])
    else:
        await state.update_data(desc=message.text)

    categories = await orm_get_categories(session)
    btns = {category["name"] : str(category["id"]) for category in categories}
    await message.answer("Choose category", reply_markup=get_callback_btns(btns=btns))
    await state.set_state(AddProduct.category)

@admin_router.callback_query(AddProduct.category)
async def add_category(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    if int(callback.data) in [category["id"] for category in await orm_get_categories(session)]:
        await callback.answer()
        await state.update_data(category=callback.data)
        await callback.message.answer("Type price of the product:")
        await state.set_state(AddProduct.price)
    else:
        await callback.message.answer("Invalid category! Choose right one to continue.")
        await callback.answer()

@admin_router.message(AddProduct.price, or_f(F.text, F.text == "."))
async def add_price(message: types.Message, state: FSMContext):
    if message.text == ".":
        await state.update_data(price=AddProduct.product_to_edit["price"])
    else:
        try:
            float(message.text)
        except ValueError:
            await message.answer("Invalid price! Type appropriate value:")
            return

        await state.update_data(price=message.text)
    await message.answer("Attach an image of your product:")
    await state.set_state(AddProduct.image)

@admin_router.message(AddProduct.image, or_f(F.photo, F.text == "."))
async def add_image(message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot):

    if message.text and message.text == ".":
        await state.update_data(image=AddProduct.product_to_edit["image"])
    else:
        await state.update_data(image=message.photo[-1].file_id)

    data = await state.get_data()

    try:
        if AddProduct.product_to_edit:
            await orm_update_product(session, AddProduct.product_to_edit["id"], data)
            await message.answer("Your product has been edited", reply_markup=ADMIN_KB)
            await log_product_edited(data=data, bot=bot)
        else:
            await orm_add_product(session=session, data=data)
            await message.answer("Your product has been added", reply_markup=ADMIN_KB)
            await log_product_added(data=data, bot=bot)
        await state.clear()
    except Exception as e:
        await message.answer(f"Something went wrong while adding your product. Report this problem", reply_markup=ADMIN_KB)
        print(str(e))
        await state.clear()

    AddProduct.product_to_edit = None

@admin_router.message(F.text == "All products")
async def add_product(message: types.Message, state: FSMContext, session: AsyncSession):
    categories = await orm_get_categories(session)
    btns = {category["name"] : f"category_{category["id"]}" for category in categories}
    await message.answer("Choose category", reply_markup=get_callback_btns(btns=btns))

@admin_router.callback_query(F.data.startswith("category_"))
async def show_products(callback: types.CallbackQuery, session: AsyncSession):
    category_id = callback.data.split("_")[-1]
    for product in await orm_get_products(session, int(category_id)):
        await callback.message.answer_photo(product.image,
                                   caption=f"<b>{product.name}</b>\n"
                                           f"<b>{product.description}</b>\n"
                                           f"Price: {round(product.price, 2)}",
                                   reply_markup=get_callback_btns(btns={
                                       "Delete":f"delete_{product.id}",
                                       "Edit":f"edit_{product.id}",
                                   }))

@admin_router.callback_query(F.data.startswith("delete_"))
async def delete_product(callback: types.CallbackQuery, session: AsyncSession, bot:Bot):
    product_id = callback.data.split("_")[-1]
    await orm_delete_product(session, int(product_id))
    await callback.message.delete()
    await callback.answer("Deleted product")
    await callback.message.answer(f"Product with <b>ID: {product_id}</b> has been deleted")
    await log_product_deleted(product_id=product_id, bot=bot)

@admin_router.callback_query(StateFilter(None), F.data.startswith("edit_"))
async def edit_product(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    product_id = callback.data.split("_")[-1]
    product_to_edit = await orm_get_product(session, int(product_id))

    AddProduct.product_to_edit = product_to_edit
    await callback.answer("Edited product")
    await callback.message.answer("Type name of the product", reply_markup=types.ReplyKeyboardRemove())

    await state.set_state(AddProduct.name)

# === FSM state to do actions with banners ===
class AddBanner(StatesGroup):
    image = State()

@admin_router.message(StateFilter(None), F.text == "Add/Edit banner")
async def add_image(message: types.Message, state: FSMContext, session: AsyncSession):
    page_names = [page["name"] for page in await orm_get_page_description(session)]
    await message.answer(f"Attach an image of your banner.\nIn description, specify for which page banner is being added.\n{', '.join(page_names)}")
    await state.set_state(AddBanner.image)

@admin_router.message(AddBanner.image, F.photo)
async def add_banner(message: types.Message, state: FSMContext, session: AsyncSession):
    image_id = message.photo[-1].file_id
    for_page = message.caption.strip()
    pages_names = [page["name"] for page in await orm_get_page_description(session)]
    if for_page not in pages_names:
        await message.answer("Invalid input! Try appropriate value.")
        return

    await orm_update_banner_image(session, for_page, image_id,)
    await message.answer("Your banner has been added/edited", reply_markup=ADMIN_KB)
    await state.clear()

@admin_router.message(Command("admin_help"))
async def admin_help(message: types.Message):
    str = f"🛑 <b>ADMIN PANNEL</b> 🛑\n"

    for index, (command, desc) in enumerate(admin_commands.items(), start=1):
        str += f"{index}) {command} - {desc}\n"

    await message.answer(str)

@admin_router.message(StateFilter(None), Command("add_employee"))
async def add_admin(message: types.Message, state: FSMContext):
    await message.answer("1️⃣ Provide new employees Telegram ID: ")
    await state.set_state(AddEmployee.user_id)

@admin_router.message(AddEmployee.user_id, or_f(F.text, F.text == "."))
async def add_user_id(message: types.Message, state: FSMContext):
    if message.text == ".":
        await state.update_data(user_id=AddEmployee.employee_to_edit["user_id"])
    else:
        try:
            int(message.text)
        except ValueError:
            await message.answer("⚠️ Invalid ID was provided! Try again.")
            return

        await state.update_data(user_id=message.text)

    await message.answer("2️⃣ Provide employees first name: ")
    await state.set_state(AddEmployee.first_name)

@admin_router.message(AddEmployee.first_name, or_f(F.text, F.text == "."))
async def add_first_name(message: types.Message, state: FSMContext):
    if message.text == ".":
        await state.update_data(first_name=AddEmployee.employee_to_edit["first_name"])
    else:
        if len(message.text) >= 20:
            await message.answer("⚠️ First name can't be more than 20 characters.")
            return

        await state.update_data(first_name=message.text)

    await message.answer("3️⃣ Provide employees last name: ")
    await state.set_state(AddEmployee.last_name)

@admin_router.message(AddEmployee.last_name, or_f(F.text, F.text == "."))
async def add_last_name(message: types.Message, state: FSMContext):
    if message.text == ".":
        await state.update_data(last_name=AddEmployee.employee_to_edit["last_name"])
    else:
        if len(message.text) >= 20:
            await message.answer("⚠️ Last name can't be more than 20 characters.")
            return

        await state.update_data(last_name=message.text)

    await message.answer("4️⃣ Provide employees phone: ")
    await state.set_state(AddEmployee.phone)

@admin_router.message(AddEmployee.phone, or_f(F.text, F.text == "."))
async def add_phone(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == ".":
        await state.update_data(phone=AddEmployee.employee_to_edit["phone"])
    else:
        if len(message.text) >= 20:
            await message.answer("⚠️ Phone can't be more than 20 characters.")
            return

        await state.update_data(phone=message.text)

    roles = await orm_get_roles(session)
    btns = {role["name"]:str(role["id"]) for role in roles}
    await message.answer("4️⃣ Choose the role of employee: ", reply_markup=get_callback_btns(btns=btns))
    await state.set_state(AddEmployee.role_id)

@admin_router.callback_query(AddEmployee.role_id)
async def add_role(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot):
    if int(callback.data) in [role["id"] for role in await orm_get_roles(session)]:
        await state.update_data(role_id=callback.data)

        data = await state.get_data()

        try:
            if AddEmployee.employee_to_edit:
                ...
            else:
                await orm_add_employee(session, data)
                await callback.message.answer("✅ New employee has been added to the shop!")
                await log_new_employee(data=data, bot=bot)
            await state.clear()
        except Exception as e:
            await callback.message.answer(f"Something went wrong while adding new employee. Report this problem")
            print(str(e))
            await state.clear()

        AddEmployee.employee_to_edit = None