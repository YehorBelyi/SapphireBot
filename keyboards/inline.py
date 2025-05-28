from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

class MenuCallBack(CallbackData, prefix="menu"):
    level: int
    menu_name: str
    category: int | None = None
    page: int = 1
    product_id: int | None = None

def get_user_main_btns(*, level:int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Shoes 👟":"catalog",
        "Cart 🛒":"cart",
        "About ℹ️":"about",
        "Payment 💵":"payment",
        "Shipping ⛴":"shipping",
    }
    for text, menu_name in btns.items():
        if menu_name == "catalog":
            keyboard.add(InlineKeyboardButton(text=text, callback_data=MenuCallBack(level=level+1, menu_name=menu_name).pack()))
        elif menu_name == "cart":
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=3, menu_name=menu_name).pack()))
        else:
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=level, menu_name=menu_name).pack()))

    return keyboard.adjust(*sizes).as_markup()

def get_user_catalog_btns(*, level:int, categories: list, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text="Go back",
                                      callback_data=MenuCallBack(level=level-1, menu_name="main").pack()))
    keyboard.add(InlineKeyboardButton(text="Cart 🛒",
                                      callback_data=MenuCallBack(level=3, menu_name="cart").pack()))

    for c in categories:
        keyboard.add(InlineKeyboardButton(text=c.name,
                                          callback_data=MenuCallBack(level=level+1, menu_name=c.name, category=c.id).pack()))

    return keyboard.adjust(*sizes).as_markup()

def get_products_btns(*,
                      level: int,
                      category: int,
                      page: int,
                      pagination_btns: dict,
                      product_id: int,
                      sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text="Go back",
                                      callback_data=MenuCallBack(level=level - 1, menu_name="main").pack()))
    keyboard.add(InlineKeyboardButton(text="Cart 🛒",
                                      callback_data=MenuCallBack(level=3, menu_name="cart").pack()))
    keyboard.add(InlineKeyboardButton(text="Order 📦",
                                      callback_data=MenuCallBack(level=level, menu_name="add_to_cart", product_id=product_id).pack()))

    keyboard.adjust(*sizes)

    row = []
    for text, menu_name in pagination_btns.items():
        if menu_name == "next":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MenuCallBack(level=level,
                                                                       menu_name=menu_name,
                                                                       category=category,
                                                                       page=page+1).pack()))
        elif menu_name == "previous":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MenuCallBack(level=level,
                                                                       menu_name=menu_name,
                                                                       category=category,
                                                                       page=page - 1).pack()))

    return keyboard.row(*row).as_markup()

def get_callback_btns(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()

def get_url_btns(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, url in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, url=url))

    return keyboard.adjust(*sizes).as_markup()

def get_mixed_btns(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, value in btns.items():
        if '://' in value:
            keyboard.add(InlineKeyboardButton(text=text, url=value))
        else:
            keyboard.add(InlineKeyboardButton(text=text, callback_data=value))

    return keyboard.adjust(*sizes).as_markup()