from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.orm_query import orm_add_product, orm_get_products

from filters.chat_types import ChatTypeFilter
from filters.admin_filter import IsAdmin
from keyboards.reply import generate_keyboard
from sqlalchemy.ext.asyncio import AsyncSession

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())



ADMIN_KB = generate_keyboard(
    "Add product", "All products",
    placeholder="Choose an action",
    sizes=(2,),
)

# Storing all steps when adding a product
class AddProduct(StatesGroup):
    name = State()
    desc = State()
    price = State()
    image = State()

    texts = {
        'AddProduct:name': 'Type name of the product again:',
        'AddProduct:desc': 'Type description of the product again:',
        'AddProduct:price': 'Type price of the product again:',
        'AddProduct:image': 'Attach image of the product again:',
    }

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

@admin_router.message(AddProduct.name, F.text)
async def add_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Type desc of the product")
    await state.set_state(AddProduct.desc)

@admin_router.message(AddProduct.desc, F.text)
async def add_desc(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text)
    await message.answer("Type price of the product:")
    await state.set_state(AddProduct.price)

@admin_router.message(AddProduct.price, F.text)
async def add_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer("Attach an image of your product:")
    await state.set_state(AddProduct.image)

@admin_router.message(AddProduct.image, F.photo)
async def add_image(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(image=message.photo[-1].file_id)
    data = await state.get_data()

    try:
        await orm_add_product(session, data)
        await message.answer("Your product has been added", reply_markup=ADMIN_KB)
        await state.clear()
    except Exception as e:
        await message.answer("Something went wrong while adding your product. Report this problem", reply_markup=ADMIN_KB)
        await state.clear()

@admin_router.message(F.text == "All products")
async def add_product(message: types.Message, state: FSMContext, session: AsyncSession):
    for product in await orm_get_products(session):
        await message.answer_photo(product.image,
                                   caption=f"<b>{product.name}</b>\n"
                                           f"<b>{product.description}</b>\n"
                                           f"Price: {round(product.price, 2)}")